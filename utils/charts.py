import plotly.express as px
from .styles import AO3_RED, NSFW_COLOR_MAP, EMOTION_COLORS
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random
import plotly.graph_objects as go

def create_tag_bar_chart(tag_df, metric):
    if tag_df is None: return px.bar(title="No Data")

    dynamic_height = 400 + (len(tag_df) * 25)
    fig = px.bar(
        tag_df, x=metric, y='tag', orientation='h',
        color_discrete_sequence=[AO3_RED], height=dynamic_height
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending', 'dtick': 1},
                      xaxis={'tickformat': ','}, template="simple_white")
    return fig


def create_fandom_stacked_chart(stats_df, top_fandoms_order):
    if stats_df is None or stats_df.empty:
        return px.bar(title="No Data")

    top_fandoms_order = [str(x) for x in top_fandoms_order]

    fig = px.bar(
        stats_df,
        x='fandom',
        y='count',
        color='is_nsfw',
        color_discrete_map=NSFW_COLOR_MAP,
        category_orders={"fandom": top_fandoms_order},
        title="Top Fandoms: SFW vs NSFW Content Split"
    )

    fig.update_layout(
        template="simple_white",
        barmode='stack',
        xaxis={'tickangle': -45},
        xaxis_title="Fandom",
        yaxis_title="Number of Works",
        legend_title="Content Type"
    )

    fig.update_xaxes(type='category')

    return fig

def ao3_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return f"hsl(0, {random.randint(80, 100)}%, {random.randint(30, 45)}%)"


def get_word_cloud_object(tag_df, metric, mask_image=None, high_res=False):
    if tag_df is None or tag_df.empty:
        return None
    data_dict = dict(zip(tag_df['tag'], tag_df[metric]))

    mask = None
    if mask_image is not None:
        img = Image.open(mask_image).convert("RGBA")
        mask_np = np.array(img)
        final_mask = np.ones(mask_np.shape[:2], dtype=np.uint8) * 255
        is_opaque = mask_np[:, :, 3] > 30
        is_not_white = (mask_np[:, :, 0] < 250) | (mask_np[:, :, 1] < 250) | (mask_np[:, :, 2] < 250)
        final_mask[is_opaque & is_not_white] = 0
        mask = final_mask

    w, h = (3840, 2160) if high_res else (1200, 900)

    return WordCloud(
        background_color="white",
        mask=mask,
        repeat=True,
        max_words=1500,
        min_font_size=4,
        max_font_size=250 if high_res else 100,
        relative_scaling=0,
        color_func=ao3_color_func,
        width=w,
        height=h,
        random_state=42
    ).generate_from_frequencies(data_dict)


def create_correlation_heatmap(corr_matrix, metric):
    if corr_matrix is None or corr_matrix.empty or (corr_matrix.values == 0).all():
        return px.imshow([[0]], title="Increase selection to see correlations.")

    display_name = metric.replace("_", " ").title()

    plot_data = corr_matrix.fillna(0)

    fig = px.imshow(
        plot_data,
        text_auto=".2f",
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        aspect="auto",
        title=f"Tag Impact Analysis: Correlation with {display_name}"
    )

    fig.update_layout(
        template="simple_white",
        xaxis=dict(tickmode='linear', tickfont=dict(size=10), tickangle=-45, automargin=True),
        yaxis=dict(tickmode='linear', tickfont=dict(size=10), automargin=True),
        height=700,
        margin=dict(l=150, r=20, t=100, b=150)
    )

    fig.add_annotation(
        text=f"<b>← Direct impact on {display_name}</b>",
        xref="paper", yref="paper",
        x=-0.1, y=1.05,
        showarrow=False,
        font=dict(size=13, color="#d92b2b"),
        align="left"
    )

    return fig


def create_emotion_bar_chart(emotion_df):
    if emotion_df is None or emotion_df.empty:
        return px.bar(title="No Sentiment Data")

    fig = px.bar(
        emotion_df, x='emotion', y='count',
        color='emotion',
        color_discrete_map=EMOTION_COLORS,
        title="Dominant Tones (Based on Work Summaries)"
    )
    fig.update_layout(template="simple_white", showlegend=False, xaxis_title="Primary Emotion (from Summary)")
    return fig

def create_emotion_radar_chart(radar_df):
    if radar_df is None or radar_df.empty:
        return go.Figure()

    dom_emo = radar_df.loc[radar_df['score'].idxmax(), 'emotion']
    color = EMOTION_COLORS.get(dom_emo, '#d92b2b')

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=radar_df['score'],
        theta=radar_df['emotion'],
        fill='toself',
        line_color=color,
        fillcolor=color,
        opacity=0.5,
        hovertemplate="<b>%{theta}</b><br>Intensity: %{r:.4f}<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=False,
                showline=False,
                ticks="",
                gridcolor="#ECECEC",
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color="#444"),
                rotation=90,
                direction="clockwise"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        height=450,
        title=dict(
            text="Emotional Fingerprint (Intensity of Summary)",
            font=dict(size=16),
            x=0.5,
            y=0.97,
            xanchor='center'
        )
    )
    return fig

def create_sentiment_success_plot(df, metric):
    if df is None or df.empty or 'top_emotion' not in df.columns:
        return px.bar()

    dff = df[df['top_emotion'] != 'neutral'].copy()
    if len(dff) > 10000: dff = dff.sample(10000)

    display_metric = metric.replace("_", " ").title()

    fig = px.box(
        dff, x='top_emotion', y=metric, color='top_emotion',
        color_discrete_map=EMOTION_COLORS,
        points=False,
        title=f"{display_metric} Distribution (Based on Summary Tone)",
        log_y=True
    )

    fig.update_layout(
        template="simple_white",
        showlegend=False,
        yaxis=dict(
            tickformat="~s",
            title=f"Total {display_metric} (Log Scale)"
        )
    )
    return fig


def get_time_series_stats(df, metric, time_unit='YE'):
    """Aggregates metrics and work counts over time."""
    if df is None or df.empty:
        return None

    dff = df.copy()
    dff['last_updated'] = pd.to_datetime(dff['last_updated'])

    dff['period'] = dff['last_updated'].dt.to_period(time_unit).dt.to_timestamp()

    stats = dff.groupby('period').agg({
        'work_id': 'count',
        metric: ['mean', 'sum']
    }).reset_index()

    stats.columns = ['period', 'work_count', f'{metric}_mean', f'{metric}_sum']
    return stats


def get_fandom_over_time(df, top_n=5):
    """Calculates how the top N fandoms have evolved over the years."""
    if df is None or df.empty: return None

    top_fandoms = df['fandom'].value_counts().head(top_n).index.tolist()
    dff = df[df['fandom'].isin(top_fandoms)].copy()
    dff['year'] = dff['last_updated'].dt.year

    stats = dff.groupby(['year', 'fandom'], observed=True).size().reset_index(name='count')
    return stats


def get_time_series_stats(df, metric, time_unit='YE'):
    """Aggregates metrics and work counts over time."""
    if df is None or df.empty:
        return None

    dff = df.copy()
    dff['last_updated'] = pd.to_datetime(dff['last_updated'])

    dff['period'] = dff['last_updated'].dt.to_period(time_unit).dt.to_timestamp()

    stats = dff.groupby('period').agg({
        'work_id': 'count',
        metric: ['mean', 'sum']
    }).reset_index()

    stats.columns = ['period', 'work_count', f'{metric}_mean', f'{metric}_sum']
    return stats


def get_fandom_over_time(df, top_n=5):
    """Calculates how the top N fandoms have evolved over the years."""
    if df is None or df.empty: return None

    top_fandoms = df['fandom'].value_counts().head(top_n).index.tolist()
    dff = df[df['fandom'].isin(top_fandoms)].copy()
    dff['year'] = dff['last_updated'].dt.year

    stats = dff.groupby(['year', 'fandom'], observed=True).size().reset_index(name='count')
    return stats


def create_metric_over_time_chart(ts_df, metric):
    if ts_df is None or ts_df.empty:
        return go.Figure()

    display_metric = metric.replace("_", " ").title()
    fig = go.Figure()

    x_axis_data = ts_df['period_str']

    fig.add_trace(go.Bar(
        x=x_axis_data,
        y=ts_df['work_count'],
        name="Number of Works",
        marker_color='rgba(180, 180, 180, 0.5)',
        yaxis='y2'
    ))

    fig.add_trace(go.Scatter(
        x=x_axis_data,
        y=ts_df[f'{metric}_mean'],
        name=f"Avg {display_metric}",
        line=dict(color='#d92b2b', width=3),
        mode='lines+markers'
    ))

    fig.update_layout(
        template="simple_white",
        title=f"Content Volume vs. Average {display_metric} Over Time",

        xaxis=dict(
            title="Timeline",
            type='date',
            tickformat='%Y',
            autorange=True
        ),

        yaxis=dict(
            title=f"Average {display_metric}",
            side="left"
        ),
        yaxis2=dict(
            title="Work Volume",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100, b=50, l=60, r=60)
    )
    return fig


def create_fandom_evolution_chart(evo_df):
    if evo_df is None or evo_df.empty: return go.Figure()

    fig = px.area(
        evo_df, x="year", y="count", color="fandom",
        title="Fandom Popularity Evolution (Work Counts)",
        line_group="fandom",
        template="simple_white"
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Works Posted/Updated")
    return fig