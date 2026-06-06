from collections import Counter, defaultdict

import pandas as pd

MAX_TAG_ROWS = 75000
MAX_CORRELATION_ROWS = 40000


def clamp_int(value, default, min_value, max_value):
    if value is None:
        return default

    try:
        value = int(value)
    except (TypeError, ValueError):
        return default

    return min(max(value, min_value), max_value)


def sample_for_tag_work(df, max_rows=MAX_TAG_ROWS):
    """Keep tag-heavy charts responsive on the full AO3 dataset."""
    if df is None or df.empty or len(df) <= max_rows:
        return df

    return df.sample(max_rows, random_state=42)


def filter_by_inputs(df, fandom_selection, date_range, nsfw_filter):
    """Filters data using the pre-calculated 'is_nsfw' column."""
    if df is None or df.empty:
        return df

    dff = df

    # 1. Fandom Filter
    if fandom_selection and "Global" not in fandom_selection:
        dff = dff[dff['fandom'].isin(fandom_selection)]

    # 2. Date Filter
    start_dt = pd.to_datetime(date_range[0])
    end_dt = pd.to_datetime(date_range[1])
    mask = (dff['last_updated'] >= start_dt) & (dff['last_updated'] <= end_dt)
    dff = dff[mask]

    # 3. NSFW Filter (Using the pre-calculated boolean column)
    if nsfw_filter == "NSFW Only":
        dff = dff[dff['is_nsfw'] == True]
    elif nsfw_filter == "SFW Only":
        dff = dff[dff['is_nsfw'] == False]

    return dff


def get_tag_stats(df, metric, top_n):
    if df is None or df.empty: return None

    top_n = clamp_int(top_n, default=20, min_value=1, max_value=100)
    df = sample_for_tag_work(df, MAX_TAG_ROWS)

    totals = Counter()
    counts = Counter()

    for tag_text, value in zip(df['additional_tags'], pd.to_numeric(df[metric], errors='coerce')):
        if pd.isna(tag_text) or tag_text == "None" or pd.isna(value):
            continue

        for tag in str(tag_text).split(', '):
            tag = tag.strip()
            if not tag:
                continue
            totals[tag] += value
            counts[tag] += 1

    if not totals:
        return None

    stats = pd.DataFrame(
        (
            (tag, total, total / counts[tag])
            for tag, total in totals.most_common(top_n)
        ),
        columns=['tag', 'total', 'average']
    )

    return stats


def get_fandom_split_stats(df, top_n):
    """Returns a DataFrame of SFW/NSFW counts and percentages per fandom."""
    if df is None or df.empty:
        return pd.DataFrame(columns=['fandom', 'is_nsfw', 'count', 'percentage']), []

    # 1. Get top N fandoms
    top_fandoms = df['fandom'].value_counts().head(top_n).index.tolist()
    dff = df[df['fandom'].isin(top_fandoms)].copy()

    # 2. Group and count
    stats = dff.groupby(['fandom', 'is_nsfw'], observed=True).size().reset_index(name='count')

    # 3. Map boolean to labels
    stats['is_nsfw'] = stats['is_nsfw'].map({True: 'NSFW', False: 'SFW'})

    # 4. Calculate Percentage (This is usually where the "cannot load" error happens)
    stats['percentage'] = stats.groupby('fandom')['count'].transform(lambda x: (x / x.sum() * 100))

    return stats, top_fandoms
def get_correlation_data(df, metric, top_n=15):
    if df is None or df.empty:
        return None

    top_n = clamp_int(top_n, default=15, min_value=2, max_value=30)
    df = sample_for_tag_work(df, MAX_CORRELATION_ROWS)

    tag_stats = get_tag_stats(df, metric, top_n)
    if tag_stats is None or tag_stats.empty:
        return None

    top_tags = tag_stats['tag'].tolist()
    top_tag_set = set(top_tags)
    id_col = 'work_id' if 'work_id' in df.columns else None

    metric_values = {}
    tag_to_ids = defaultdict(set)

    ids = df[id_col] if id_col else df.index
    values = pd.to_numeric(df[metric], errors='coerce')

    for row_id, tag_text, value in zip(ids, df['additional_tags'], values):
        if pd.isna(tag_text) or tag_text == "None" or pd.isna(value):
            continue

        matched_tags = set()
        for tag in str(tag_text).split(', '):
            tag = tag.strip()
            if tag in top_tag_set:
                matched_tags.add(tag)

        if not matched_tags:
            continue

        metric_values[row_id] = value
        for tag in matched_tags:
            tag_to_ids[tag].add(row_id)

    if not metric_values:
        return None

    work_ids = list(metric_values.keys())
    binary_matrix = pd.DataFrame(0, index=work_ids, columns=top_tags, dtype='uint8')

    for tag, row_ids in tag_to_ids.items():
        binary_matrix.loc[list(row_ids), tag] = 1

    metric_series = pd.Series(metric_values, name=metric)
    combined_df = binary_matrix.join(metric_series)
    corr_matrix = combined_df.corr().fillna(0)

    if metric in corr_matrix.columns:
        ordered_list = [metric] + [tag for tag in top_tags if tag in corr_matrix.columns]
        corr_matrix = corr_matrix.loc[ordered_list, ordered_list]

    return corr_matrix


def get_emotion_stats(df):
    """Returns the count of works for each dominant emotion."""
    if df is None or df.empty or 'top_emotion' not in df.columns:
        return None

    stats = df['top_emotion'].value_counts().reset_index()
    stats.columns = ['emotion', 'count']

    stats = stats[stats['emotion'] != 'neutral']
    return stats


def get_emotional_radar_data(df):
    """Calculates the average intensity of each emotion for the radar chart."""
    if df is None or df.empty:
        return None

    emotions = ['fear', 'anger', 'trust', 'surprise', 'sadness', 'disgust', 'joy', 'anticipation']
    emo_cols = [f'emo_{e}' for e in emotions]

    existing_cols = [c for c in emo_cols if c in df.columns]
    if not existing_cols: return None

    avg_scores = df[existing_cols].mean().reset_index()
    avg_scores.columns = ['emotion', 'score']
    avg_scores['emotion'] = avg_scores['emotion'].str.replace('emo_', '')

    return avg_scores


def get_time_series_stats(df, metric, time_unit='Y'):
    if df is None or df.empty:
        return None

    dff = df.copy()

    dff[metric] = pd.to_numeric(dff[metric], errors='coerce')
    dff['last_updated'] = pd.to_datetime(dff['last_updated'])
    dff = dff.dropna(subset=[metric, 'last_updated'])

    # 1. Group by the time period
    dff['temp_period'] = dff['last_updated'].dt.to_period(time_unit).dt.to_timestamp()

    stats = dff.groupby('temp_period').agg({
        'work_id': 'count',
        metric: ['mean', 'sum']
    }).reset_index()

    # 2. Clean up columns
    stats.columns = ['period', 'work_count', f'{metric}_mean', f'{metric}_sum']

    # 3. Convert the date objects into standard ISO strings ('2024-01-01')
    stats['period_str'] = stats['period'].dt.strftime('%Y-%m-%d')

    return stats.sort_values('period')


def get_fandom_over_time(df, top_n=5):
    """Calculates how the top N fandoms have evolved over the years."""
    if df is None or df.empty: return None

    top_fandoms = df['fandom'].value_counts().head(top_n).index.tolist()
    dff = df[df['fandom'].isin(top_fandoms)].copy()
    dff['year'] = dff['last_updated'].dt.year

    stats = dff.groupby(['year', 'fandom'], observed=True).size().reset_index(name='count')
    return stats
