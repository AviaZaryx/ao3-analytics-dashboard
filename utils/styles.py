# AO3 Brand Colors
AO3_RED = "#9f1d20"
AO3_DARK_RED = "#781214"
AO3_INK = "#1f1f24"
AO3_MUTED = "#64646f"
BG_LIGHT = "#f6f4f1"

# Custom CSS
CSS = f"""
    :root {{
        --ao3-red: {AO3_RED};
        --ao3-dark-red: {AO3_DARK_RED};
        --ao3-ink: {AO3_INK};
        --ao3-muted: {AO3_MUTED};
        --ao3-bg: {BG_LIGHT};
        --ao3-panel: #ffffff;
        --ao3-border: #ded7cf;
    }}

    body {{
        background: var(--ao3-bg);
        color: var(--ao3-ink);
        font-family: Inter, "Segoe UI", Arial, sans-serif;
        font-size: 0.95rem;
    }}

    .navbar {{
        background-color: var(--ao3-red) !important;
        border-bottom: 1px solid var(--ao3-dark-red);
        box-shadow: 0 2px 10px rgba(31, 31, 36, 0.14);
        min-height: 48px;
    }}

    .navbar-brand {{
        color: #fff !important;
        font-weight: 700;
        letter-spacing: 0;
    }}

    .app-title {{
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        color: #fff;
        font-weight: 750;
        line-height: 1;
    }}

    .app-title-logo {{
        width: 26px;
        height: 26px;
        object-fit: contain;
        background: #fff;
        border-radius: 50%;
        padding: 3px;
        box-shadow: 0 1px 4px rgba(31, 31, 36, 0.18);
    }}

    .bslib-sidebar-layout {{
        gap: 1rem;
    }}

    .sidebar {{
        background: #f0ebe5;
        border-right: 1px solid var(--ao3-border);
        box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.55);
    }}

    .sidebar .sidebar-title {{
        color: var(--ao3-ink);
        font-size: 0.92rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .sidebar h3 {{
        color: var(--ao3-ink);
        font-size: 1rem;
        font-weight: 700;
        margin: 1.4rem 0 0.75rem;
    }}

    .sidebar hr {{
        border-color: #d8d0c8;
        opacity: 1;
        margin: 1.4rem 0;
    }}

    label, .control-label {{
        color: #3f3f47;
        font-size: 0.82rem;
        font-weight: 650;
        margin-bottom: 0.35rem;
    }}

    .form-control, .form-select, .selectize-input {{
        border: 1px solid #cfc7bf !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        min-height: 36px;
    }}

    .form-control:focus, .form-select:focus, .selectize-input.focus {{
        border-color: var(--ao3-red) !important;
        box-shadow: 0 0 0 3px rgba(159, 29, 32, 0.12) !important;
    }}

    .irs--shiny .irs-bar,
    .irs--shiny .irs-single,
    .irs--shiny .irs-from,
    .irs--shiny .irs-to {{
        background: var(--ao3-red);
        border-color: var(--ao3-red);
    }}

    .irs--shiny .irs-handle {{
        border-color: var(--ao3-red);
        background: #fff;
    }}

    .nav-tabs {{
        border-bottom: 1px solid #d8d0c8;
        gap: 0.2rem;
        margin-bottom: 0.75rem;
    }}

    .nav-tabs .nav-link {{
        border: 0;
        border-radius: 6px 6px 0 0;
        color: #315d83;
        font-size: 0.9rem;
        font-weight: 650;
        padding: 0.65rem 0.9rem;
    }}

    .nav-tabs .nav-link:hover {{
        background: #eee8e2;
        color: var(--ao3-dark-red);
    }}

    .nav-tabs .nav-link.active {{
        background: var(--ao3-panel);
        color: var(--ao3-red);
        border: 1px solid #d8d0c8;
        border-bottom-color: var(--ao3-panel);
        box-shadow: 0 -2px 8px rgba(31, 31, 36, 0.04);
    }}

    .card {{
        background: var(--ao3-panel);
        border: 1px solid #e0d9d1;
        border-radius: 8px;
        box-shadow: 0 8px 22px rgba(31, 31, 36, 0.08);
        overflow: hidden;
    }}

    .card-header {{
        background-color: var(--ao3-red);
        color: white;
        border-bottom: 0;
        font-weight: 750;
        padding: 0.72rem 0.95rem;
    }}

    .card-body {{
        padding: 0.95rem;
    }}

    .btn-primary {{
        background-color: var(--ao3-red);
        border-color: var(--ao3-dark-red);
        border-radius: 6px;
        font-weight: 650;
    }}

    .btn-primary:hover {{
        background-color: var(--ao3-dark-red);
    }}

    blockquote {{
        border-left: 4px solid var(--ao3-red);
        background: #fffaf5;
        color: var(--ao3-muted);
        padding: 0.75rem 1rem;
        margin: 0 0 1rem;
    }}

    .card > .markdown, .card p, .card li {{
        color: #383840;
        line-height: 1.55;
    }}

    .cluster-card {{
        border: 1px solid #e0d9d1;
        box-shadow: 0 10px 24px rgba(31, 31, 36, 0.08);
    }}

    .cluster-card .card-header {{
        align-items: center;
    }}

    .cluster-meta {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.85rem 1rem 0.35rem;
        color: var(--ao3-muted);
        font-size: 0.9rem;
    }}

    .cluster-meta span:last-child {{
        color: var(--ao3-red);
        font-weight: 700;
        white-space: nowrap;
    }}

    .cluster-plot-wrap {{
        padding: 0 0.85rem 0.85rem;
    }}
"""

SFW_BLUE = "#2f6f9f"
NSFW_PINK = "#c84f7c"

# Color Map for the charts
NSFW_COLOR_MAP = {
    "SFW": SFW_BLUE,
    "NSFW": NSFW_PINK
}

EMOTION_COLORS = {
    'joy': '#f0b429',
    'sadness': '#4d7ea8',
    'anger': '#b23a48',
    'fear': '#5b4b8a',
    'surprise': '#d66ba0',
    'trust': '#5f9f7a',
    'disgust': '#8a5a44',
    'anticipation': '#d9822b',
    'neutral': '#c7c7c7'
}
