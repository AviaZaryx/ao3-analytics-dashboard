import base64
import io
import os
from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
from datetime import timedelta

# Import modules
from utils.data_loader import load_clean_data
from utils.data_processing import filter_by_inputs, get_tag_stats, get_fandom_split_stats, get_correlation_data, \
    get_emotion_stats, get_emotional_radar_data, get_time_series_stats, get_fandom_over_time
from utils.charts import create_tag_bar_chart, create_fandom_stacked_chart, get_word_cloud_object, \
    create_correlation_heatmap, create_emotion_bar_chart, create_emotion_radar_chart, create_sentiment_success_plot, \
    create_fandom_evolution_chart, create_metric_over_time_chart
from utils.styles import CSS

# --- INITIALIZATION ---
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_ao3_data.csv")
NSFW_PATH = os.path.join(BASE_DIR, "data", "nsfw", "nsfw_works.csv")
LOGO_PATH = r"D:\Downloads\DataVisProj2\Logo_Archive_of_Our_Own.svg.png"

df, fandom_map, min_date_val, max_date_val = load_clean_data(DATA_PATH, NSFW_PATH)

if min_date_val == max_date_val:
    print("WARNING: Min and Max dates are equal. Adjusting to prevent crash.")
    max_date_val = min_date_val + timedelta(days=1)

# --- JAVASCRIPT ---
js_logic = """
Shiny.addCustomMessageHandler('prepare_image', function(message) {
    const base64Data = message.base64;

    const viewerHtml = `
        <html>
        <head>
            <title>AO3 Word Cloud Viewer</title>
            <style>
                body { margin: 0; padding: 0; overflow: hidden; background: #121212; font-family: sans-serif; color: white; }
                #viewer-container { width: 100vw; height: 100vh; cursor: grab; display: flex; align-items: center; justify-content: center; position: relative; }
                #viewer-container:active { cursor: grabbing; }
                img { max-width: none; transform-origin: 0 0; transition: transform 0.05s linear; }
                #ui-overlay { 
                    position: fixed; top: 20px; left: 20px; background: rgba(0,0,0,0.85); 
                    color: white; padding: 20px; border-radius: 12px; border: 1px solid #444;
                    pointer-events: none; z-index: 100; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                }
                .key { background: #d92b2b; color: white; padding: 2px 8px; border-radius: 4px; margin-right: 10px; font-weight: bold; font-family: monospace; }
            </style>
        </head>
        <body>
            <div id="ui-overlay">
                <div style="font-weight: bold; color: #ff4d4d; font-size: 18px; margin-bottom: 10px;">AO3 4K Viewer</div>
                <div style="margin-bottom:5px;"><span class="key">SCROLL</span> Zoom In/Out</div>
                <div style="margin-bottom:5px;"><span class="key">DRAG</span> Move Image</div>
                <div><span class="key">DBL-CLICK</span> Reset View</div>
            </div>
            <div id="viewer-container"><img id="cloud-img" src="${base64Data}" /></div>
            <script>
                const img = document.getElementById('cloud-img');
                const container = document.getElementById('viewer-container');
                let scale = 0.4; let pos = { x: window.innerWidth/4, y: 50 };
                let isDragging = false; let startPos = { x: 0, y: 0 };
                function draw() { img.style.transform = 'translate(' + pos.x + 'px, ' + pos.y + 'px) scale(' + scale + ')'; }
                window.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    const delta = e.deltaY > 0 ? 0.9 : 1.1;
                    pos.x = e.clientX - (e.clientX - pos.x) * delta;
                    pos.y = e.clientY - (e.clientY - pos.y) * delta;
                    scale *= delta; draw();
                }, { passive: false });
                container.onmousedown = (e) => { isDragging = true; startPos = { x: e.clientX - pos.x, y: e.clientY - pos.y }; };
                window.onmousemove = (e) => { if (!isDragging) return; pos.x = e.clientX - startPos.x; pos.y = e.clientY - startPos.y; draw(); };
                window.onmouseup = () => isDragging = false;
                window.ondblclick = () => { scale = 0.4; pos = { x: window.innerWidth/4, y: 50 }; draw(); };
                draw();
            <\/script>
        </body>
        </html>
    `;

    const blob = new Blob([viewerHtml], {type: 'text/html'});
    const blobUrl = URL.createObjectURL(blob);

    const checkExist = setInterval(function() {
       const link = document.getElementById('ready_image_link');
       if (link) {
          link.href = blobUrl;
          clearInterval(checkExist);
       }
    }, 100);
});
"""

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
        ui.input_numeric("top_n_tags", "Top N Tags (Bar Chart):", value=20),
        ui.input_slider("top_n_fandoms", "Top N Fandoms:", min=5, max=50, value=10),
        ui.hr(),
        ui.markdown("### Word Cloud Tools"),
        ui.input_action_button("open_cloud_btn", "Open High-Res in New Tab", class_="btn-danger w-100"),
        ui.help_text("Opens a 4K image in a separate interactive viewer tab."),
        title="Controls",
        width=350,
        open="always"
    ),

    ui.head_content(
        ui.tags.script(ui.HTML(js_logic)),
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
                ui.card_header(
                    ui.div("SFW vs NSFW Comparison"),
                    ui.div(ui.output_ui("tag_count_refy"), style="font-weight: normal; opacity: 0.8;"),
                    style="display: flex; justify-content: space-between; align-items: center; width: 100%;"
                ),
                output_widget("fandom_split_chart"),
                full_screen=True
            )
        ),
        ui.nav_panel(
            "Word Cloud",
            ui.card(
                ui.card_header("Preview"),
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
                width=1 / 2  # This puts the first two side-by-side
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
                    ui.markdown("Shows how the volume of top fandoms has changed over time."),
                    output_widget("fandom_evolution_chart"),
                    full_screen=True
                ),
                width=1
            )
        ),
    ),
    title="AO3 Analytics Dashboard"
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
    def tag_count_refy():
        return f"{len(tag_data()):,} works"

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
    def fandom_split_chart():
        d = filter_by_inputs(df, input.fandom_select(), input.date_range(), "All")
        stats, order = get_fandom_split_stats(d, input.top_n_fandoms())
        return create_fandom_stacked_chart(stats, order)

    @output
    @render.plot
    def word_cloud_preview():
        d = tag_data()
        stats = get_tag_stats(d, input.metric(), 100)
        mask = LOGO_PATH if os.path.exists(LOGO_PATH) else None
        wc = get_word_cloud_object(stats, input.metric(), mask, high_res=False)
        if not wc: return None
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        return fig

    @reactive.effect
    @reactive.event(input.open_cloud_btn)
    async def _():
        with ui.Progress(min=1, max=1) as p:
            p.set(message="Generating 4K Image...", detail="Opening separate viewer tab...")
            d = tag_data()
            stats = get_tag_stats(d, input.metric(), 250)
            mask = LOGO_PATH if os.path.exists(LOGO_PATH) else None
            wc = get_word_cloud_object(stats, input.metric(), mask, high_res=True)

            img = wc.to_image()
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            base64_url = f"data:image/png;base64,{img_str}"

            m = ui.modal(
                ui.div(
                    ui.markdown("### High-Res Viewer Ready"),
                    ui.tags.a(
                        "CLICK HERE TO OPEN VIEWER",
                        id="ready_image_link",
                        href="#",
                        target="_blank",
                        class_="btn btn-danger btn-lg w-100",
                        style="text-decoration: none; color: white; font-weight: bold;"
                    ),
                    style="text-align: center; padding: 25px;"
                ),
                title="Render Complete",
                easy_close=True,
                footer=ui.modal_button("Cancel")
            )
            ui.modal_show(m)

            await session.send_custom_message('prepare_image', {'base64': base64_url})

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
        stats = get_fandom_over_time(d, top_n=5)
        return create_fandom_evolution_chart(stats)

app = App(app_ui, server)

# shiny run app.py