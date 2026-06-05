import pandas as pd

def filter_by_inputs(df, fandom_selection, date_range, nsfw_filter):
    """Filters data using the pre-calculated 'is_nsfw' column."""
    if df is None or df.empty:
        return df

    dff = df.copy()

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
    """Returns a DataFrame of the top N tags."""
    if df is None or df.empty: return None

    tags_df = df[df['additional_tags'].notna() & (df['additional_tags'] != "None")].copy()
    tags_expanded = tags_df.assign(tag=tags_df['additional_tags'].str.split(', ')).explode('tag')
    tags_expanded['tag'] = tags_expanded['tag'].str.strip()

    return (tags_expanded.groupby('tag')[metric].sum()
            .sort_values(ascending=False).head(top_n).reset_index())


def get_fandom_split_stats(df, top_n):
    """Returns a DataFrame of SFW/NSFW counts per fandom."""
    if df is None or df.empty: return None, []

    # 1. Get the top N fandoms based on current filter
    top_fandoms = df['fandom'].value_counts().head(top_n).index.tolist()

    # 2. Filter to only those fandoms
    dff = df[df['fandom'].isin(top_fandoms)].copy()

    # --- THE FIX ---
    # If the column is a category, we must remove the unused ones
    # so Plotly doesn't try to draw 10,000 empty bars.
    if hasattr(dff['fandom'], 'cat'):
        dff['fandom'] = dff['fandom'].cat.remove_unused_categories()
    # ----------------

    # 3. Group and count
    stats = dff.groupby(['fandom', 'is_nsfw'], observed=True).size().reset_index(name='count')

    # 4. Map boolean to labels
    stats['is_nsfw'] = stats['is_nsfw'].map({True: 'NSFW', False: 'SFW'})

    return stats, top_fandoms

def get_correlation_data(df, metric, top_n=15):
    if df is None or df.empty:
        return None

    # 1. Replicate Explosion
    tags_df = df[df['additional_tags'].notna() & (df['additional_tags'] != "None")].copy()
    tags_expanded = tags_df.assign(tag=tags_df['additional_tags'].str.split(', ')).explode('tag')
    tags_expanded['tag'] = tags_expanded['tag'].str.strip()

    # 2. Identify Top N Tags sorted by Metric Sum (This is your "Bar Chart order")
    top_tags_stats = (tags_expanded.groupby('tag')[metric].sum()
                      .sort_values(ascending=False).head(top_n))
    top_tags = top_tags_stats.index.tolist() # This list is now [Rank 1, Rank 2, Rank 3...]

    # 3. Filter data
    subset = tags_expanded[tags_expanded['tag'].isin(top_tags)].copy()

    # 4. Identify Work ID
    id_col = 'work_id' if 'work_id' in subset.columns else subset.index.name
    if not id_col:
        id_col = 'index'
        subset = subset.reset_index()

    # 5. Create Binary Matrix
    binary_matrix = subset.groupby([id_col, 'tag']).size().unstack(fill_value=0)
    binary_matrix = (binary_matrix > 0).astype(int)

    # 6. Attach Metric
    metric_values = subset.groupby(id_col)[metric].max()
    combined_df = binary_matrix.join(metric_values)

    # 7. Calculate Correlation
    corr_matrix = combined_df.corr().fillna(0)

    # 8. ENFORCE SORT ORDER
    # We want the Metric first, then tags in the order they appear in the bar chart
    if metric in corr_matrix.columns:
        # Create the specific order: [metric, Top Tag 1, Top Tag 2, ...]
        ordered_list = [metric] + [tag for tag in top_tags if tag in corr_matrix.columns]
        # Re-index both rows and columns to match this order
        corr_matrix = corr_matrix.loc[ordered_list, ordered_list]

    return corr_matrix


def get_emotion_stats(df):
    """Returns the count of works for each dominant emotion."""
    if df is None or df.empty or 'top_emotion' not in df.columns:
        return None

    # Count occurrences of each emotion
    stats = df['top_emotion'].value_counts().reset_index()
    stats.columns = ['emotion', 'count']

    # Filter out 'neutral' if you want a cleaner 'Emotional' look
    stats = stats[stats['emotion'] != 'neutral']
    return stats


def get_emotional_radar_data(df):
    """Calculates the average intensity of each emotion for the radar chart."""
    if df is None or df.empty:
        return None

    emotions = ['fear', 'anger', 'trust', 'surprise', 'sadness', 'disgust', 'joy', 'anticipation']
    # Select the emo_ columns and calculate the mean
    emo_cols = [f'emo_{e}' for e in emotions]

    # Ensure columns exist before calculating
    existing_cols = [c for c in emo_cols if c in df.columns]
    if not existing_cols: return None

    avg_scores = df[existing_cols].mean().reset_index()
    avg_scores.columns = ['emotion', 'score']
    # Clean up the names (remove 'emo_')
    avg_scores['emotion'] = avg_scores['emotion'].str.replace('emo_', '')

    return avg_scores


def get_time_series_stats(df, metric, time_unit='Y'):
    if df is None or df.empty:
        return None

    dff = df.copy()

    # Ensure numeric types (matching your clean.py logic)
    dff[metric] = pd.to_numeric(dff[metric], errors='coerce')
    dff['last_updated'] = pd.to_datetime(dff['last_updated'])
    dff = dff.dropna(subset=[metric, 'last_updated'])

    # 1. Group by the time period
    # We create a temporary column for grouping
    dff['temp_period'] = dff['last_updated'].dt.to_period(time_unit).dt.to_timestamp()

    stats = dff.groupby('temp_period').agg({
        'work_id': 'count',
        metric: ['mean', 'sum']
    }).reset_index()

    # 2. Clean up columns
    stats.columns = ['period', 'work_count', f'{metric}_mean', f'{metric}_sum']

    # 3. THE FIX: Convert the date objects into standard ISO strings ('2024-01-01')
    # This forces Plotly to stop using scientific notation (10^18)
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