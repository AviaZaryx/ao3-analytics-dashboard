import base64
import io
import os
from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
from datetime import timedelta
import matplotlib.pyplot as plt

# Import modules
from utils.data_loader import load_clean_data
from utils.data_processing import filter_by_inputs, get_tag_stats, get_fandom_split_stats, get_correlation_data, \
    get_emotion_stats, get_emotional_radar_data, get_time_series_stats, get_fandom_over_time
from utils.charts import create_tag_bar_chart, create_fandom_stacked_chart, get_word_cloud_object, \
    create_correlation_heatmap, create_emotion_bar_chart, create_emotion_radar_chart, create_sentiment_success_plot, \
    create_fandom_evolution_chart, create_metric_over_time_chart, create_cluster_scatter_plot
from utils.styles import CSS

# --- INITIALIZATION ---
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_ao3_data.csv")
NSFW_PATH = os.path.join(BASE_DIR, "data", "nsfw", "nsfw_works.csv")
LOGO_PATH = os.path.join(BASE_DIR, "Logo_Archive_of_Our_Own.svg.png")


def image_data_uri(path):
    if not os.path.exists(path):
        return ""

    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")

    return f"data:image/png;base64,{encoded}"


LOGO_URI = image_data_uri(LOGO_PATH)

df, fandom_map, min_date_val, max_date_val = load_clean_data(DATA_PATH, NSFW_PATH)

# --- UI ---
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.markdown("### Fandom Filter"),
        ui.input_selectize("fandom_select", "Select Fandom(s):",
                           choices={"Global": "Global (All Fandoms)"} | fandom_map,
                           multiple=True),
        ui.input_slider("date_range", "Date Range:", min=min_date_val, max=max_date_val,
                        value=[min_date_val, max_date_val]),
        ui.hr(),
        ui.markdown("### Analysis Settings"),
        ui.input_radio_buttons("nsfw_filter", "Content Filter:",
                               choices=["All", "SFW Only", "NSFW Only"],
                               selected="All", inline=True),
        ui.input_select("metric", "Metric:",
                        choices={"hits": "Hits", "kudos": "Kudos", "bookmarks": "Bookmarks",
                                 "comments": "Comments", "word_count": "Word Count"}),
        ui.input_numeric("top_n_tags", "Top N Tags (Bar Chart):", value=20, min=5, max=50),
        ui.input_slider("top_n_fandoms", "Top N Fandoms:", min=5, max=50, value=10),

        ui.hr(),
        ui.markdown("### Word Cloud Tools"),
        ui.input_select("wc_shape", "Word Cloud Shape:",
                        choices=["Simple Circle", "AO3 Logo"]),

        ui.hr(),
        ui.markdown("### Percentage of points (ML)"),
        ui.input_select("percentage", "Percentage:",
                        choices=["1%", "2%", "5%", "10%", "20%", "50%", "100%"]),

        title="Controls",
        width=350,
        open="always"
    ),

    ui.head_content(
        ui.tags.link(rel="icon", type="image/png", href=LOGO_URI),
        ui.tags.link(rel="shortcut icon", type="image/png", href=LOGO_URI),
        ui.tags.link(rel="apple-touch-icon", href=LOGO_URI),
        ui.tags.style(CSS)
    ),

    ui.navset_tab(
        ui.nav_panel(
            "Tag Analysis",
            ui.card(
                ui.card_header(
                    ui.div(
                        ui.div(ui.output_ui("dynamic_tag_title")),
                        ui.div(ui.output_ui("tag_count_ref"), style="font-weight: normal; opacity: 0.8;"),
                        style="display: flex; justify-content: space-between; align-items: center; width: 100%;"
                    )
                ),
                ui.output_ui("tags_plot_container"),
                full_screen=True
            )
        ),
        ui.nav_panel(
            "Fandom Distribution",
            ui.card(
                ui.markdown(
                    """
                    ### Content Definitions
                    *   **SFW (Safe For Work):** Works rated 'General Audiences' or 'Teen And Up Audiences'. Generally focus on plot, romance, or platonic themes without explicit sexual content.
                    *   **NSFW (Not Safe For Work):** Works rated 'Mature' or 'Explicit'. Often contain graphic violence or explicit sexual content.
                    """
                ),
                style="background-color: #f8f9fa; border-left: 5px solid #d92b2b;"
            ),

            ui.layout_column_wrap(
                ui.card(
                    ui.card_header(
                        "Content Volume",
                        ui.div(
                            ui.div(ui.output_ui("tag_count_ref1"), style="font-weight: normal; opacity: 0.8;"),
                            style="display: flex; justify-content: flex-end; align-items: center; width: 100%;"
                        )
                    ),
                    output_widget("fandom_volume_chart"),
                    full_screen=True
                ),
                ui.card(
                    ui.card_header("Content Ratio",
                        ui.div(
                            ui.div(ui.output_ui("tag_count_ref2"), style="font-weight: normal; opacity: 0.8;"),
                            style="display: flex; justify-content: flex-end; align-items: center; width: 100%;"
                        )
                    ),
                    output_widget("fandom_ratio_chart"),
                    full_screen=True
                ),
                width=1 / 2
            )
        ),
        ui.nav_panel(
            "Word Cloud",
            ui.card(
                ui.card_header("Word Cloud"),
                ui.output_plot("word_cloud_preview", height="800px"),
                full_screen=True
            )
        ),
        ui.nav_panel(
            "Impact Analysis",
            ui.card(
                ui.card_header("Tag Correlation Matrix"),
                ui.markdown("""
                    **How to read this:** Values closer to **1.0 (Red)** mean the tag (or pair of tags) 
                    strongly correlates with higher success in the chosen metric. 
                    Values near **0** mean no relationship.
                """),
                output_widget("correlation_chart"),
                full_screen=True
            )
        ),
        ui.nav_panel(
            "Sentiment Profile",
            ui.markdown("""
                    > **Note:** This analysis is performed on work summaries only, 
                    not the full body text. It represents the "hook" or intended vibe presented by the author.
                """),
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Dominant Emotion Counts"),
                    ui.markdown("Counts how many works have each emotion as their single strongest primary tone."),
                    output_widget("emotion_chart"),
                    full_screen=True
                ),
                ui.card(
                    ui.card_header("Emotional Fingerprint"),
                    ui.markdown("Measures the total score of every emotion, showing the collective atmosphere of the fandom."),
                    output_widget("radar_chart"),
                    full_screen=True
                ),
                width=1 / 2
            ),
            ui.card(
                ui.card_header("Impact on Success"),
                ui.markdown("Compares the median success of works to see which primary emotions drive the most reader engagement."),
                output_widget("sentiment_success_chart"),
                full_screen=True
            )
        ),
        ui.nav_panel(
            "Temporal Trends",
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Growth & Engagement Over Time"),
                    ui.input_select("time_unit", "Time Resolution:",
                                    choices={"Y": "Yearly", "M": "Monthly"}),
                    output_widget("time_series_chart"),
                    full_screen=True
                ),
                ui.card(
                    ui.card_header("Fandom Landscape Shift"),
                    ui.input_slider("numFan", "Fandoms:", min=5, max=50, value=10),
                    ui.markdown("Shows how the volume of top fandoms has changed over time."),
                    output_widget("fandom_evolution_chart"),
                    full_screen=True
                ),
                width=1
            )
        ),
        ui.nav_panel(
            "Clustering (ML)",
            ui.card(
                ui.card_header("Works Clustering",
                    ui.div(
                        ui.div(ui.output_ui("tag_count_ref3"), style="font-weight: normal; opacity: 0.8;"),
                        style="display: flex; justify-content: flex-end; align-items: center; width: 100%;"
                    )
                ),
                ui.div(
                    ui.span("PCA map of semantically related works"),
                    ui.span(ui.output_ui("cluster_sample_note")),
                    class_="cluster-meta"
                ),
                ui.div(output_widget("ml_cluster_chart"), class_="cluster-plot-wrap"),
                full_screen=True,
                class_="cluster-card"
            )
        ),
    ),
    title=ui.div(
        ui.img(src=LOGO_URI, alt="AO3 logo", class_="app-title-logo"),
        ui.span("AO3 Analytics Dashboard"),
        class_="app-title"
    )
)


def server(input, output, session):
    @reactive.calc
    def tag_data():
        return filter_by_inputs(df, input.fandom_select(), input.date_range(), input.nsfw_filter())

    @output
    @render.ui
    def dynamic_tag_title():
        m = input.metric().replace("_", " ").title()
        return f"Top Tags by Total {m}"

    @output
    @render.ui
    def tag_count_ref():
        return f"{len(tag_data()):,} works"

    @output
    @render.ui
    def tag_count_ref1():
        return f"{len(tag_data()):,} works"

    @output
    @render.ui
    def tag_count_ref2():
        return f"{len(tag_data()):,} works"

    @output
    @render.ui
    def tag_count_ref3():
        percentage = input.percentage() or "1%"
        try:
            percent = int(str(percentage).replace("%", ""))
        except ValueError:
            percent = 1

        percent = min(max(percent, 1), 100)
        return f"{round((percent / 100) * len(tag_data())):,} works"

    @output
    @render.ui
    def cluster_sample_note():
        percentage = input.percentage() or "1%"
        return f"{percentage} sample"

    @output
    @render.ui
    def tags_plot_container():
        return output_widget("tags_chart")

    @output
    @render_widget
    def tags_chart():
        d = tag_data()
        stats = get_tag_stats(d, input.metric(), input.top_n_tags())
        return create_tag_bar_chart(stats, input.metric())

    @output
    @render_widget
    def fandom_volume_chart():
        d = filter_by_inputs(df, input.fandom_select(), input.date_range(), "All")
        stats, order = get_fandom_split_stats(d, input.top_n_fandoms())
        return create_fandom_stacked_chart(stats, order, mode="count")

    @output
    @render_widget
    def fandom_ratio_chart():
        d = filter_by_inputs(df, input.fandom_select(), input.date_range(), "All")
        stats, order = get_fandom_split_stats(d, input.top_n_fandoms())
        return create_fandom_stacked_chart(stats, order, mode="relative")

    @output
    @render.plot
    def word_cloud_preview():
        d = tag_data()
        stats = get_tag_stats(d, input.metric(), 150)

        wc = get_word_cloud_object(stats, input.wc_shape(), LOGO_PATH, high_res=False)

        if not wc: return None
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        return fig

    @output
    @render_widget
    def correlation_chart():
        d = tag_data()

        corr_matrix = get_correlation_data(d, input.metric(), input.top_n_tags())

        return create_correlation_heatmap(corr_matrix, input.metric())

    @output
    @render_widget
    def emotion_chart():
        d = tag_data()
        stats = get_emotion_stats(d)
        return create_emotion_bar_chart(stats)

    @output
    @render_widget
    def radar_chart():
        d = tag_data()
        radar_stats = get_emotional_radar_data(d)
        return create_emotion_radar_chart(radar_stats)

    @output
    @render_widget
    def sentiment_success_chart():
        d = tag_data()
        return create_sentiment_success_plot(d, input.metric())

    @output
    @render_widget
    def time_series_chart():
        d = tag_data()
        stats = get_time_series_stats(d, input.metric(), input.time_unit())
        return create_metric_over_time_chart(stats, input.metric())

    @output
    @render_widget
    def fandom_evolution_chart():
        d = tag_data()

        if d is None or d.empty:
            return None

        n_fandoms = int(input.numFan())

        stats = get_fandom_over_time(d, top_n=n_fandoms)
        return create_fandom_evolution_chart(stats)

    @output
    @render_widget
    def ml_cluster_chart():
        d = tag_data()
        return create_cluster_scatter_plot(d, input.percentage())

app = App(app_ui, server)

# shiny run app.py
