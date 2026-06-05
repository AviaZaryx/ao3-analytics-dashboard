# AO3 Brand Colors
AO3_RED = "#990000"
AO3_DARK_RED = "#770000"
BG_LIGHT = "#f4f4f4"

# Custom CSS
CSS = f"""
    body {{ background-color: {BG_LIGHT}; }}
    .navbar {{ background-color: {AO3_RED} !important; color: white; }}
    .btn-primary {{ background-color: {AO3_RED}; border-color: {AO3_DARK_RED}; }}
    .btn-primary:hover {{ background-color: {AO3_DARK_RED}; }}
    .card-header {{ background-color: {AO3_RED}; color: white; font-weight: bold; }}
    .sidebar {{ border-right: 2px solid {AO3_RED}; }}
"""

SFW_BLUE = "#2e6da4"  # A nice standard blue
NSFW_PINK = "#e6608e"  # A soft pink/red for NSFW

# Color Map for the charts
NSFW_COLOR_MAP = {
    "SFW": SFW_BLUE,
    "NSFW": NSFW_PINK
}

EMOTION_COLORS = {
    'joy': '#FFD700',          # Gold
    'sadness': '#4682B4',      # Steel Blue
    'anger': '#B22222',        # Firebrick
    'fear': '#483D8B',         # Dark Slate Blue
    'surprise': '#FF69B4',     # Hot Pink
    'trust': '#90EE90',        # Light Green
    'disgust': '#8B4513',      # Saddle Brown
    'anticipation': '#FF8C00', # Dark Orange
    'neutral': '#D3D3D3'       # Light Grey
}