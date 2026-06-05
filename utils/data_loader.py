import pandas as pd
import os
from datetime import date


def load_clean_data(file_path, nsfw_file_path):
    """Loads processed sentiment data and cross-references NSFW IDs."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return pd.DataFrame(), {}, date(2000, 1, 1), date.today()

    try:
        # Define dtypes for ALL columns to save memory (especially with 900k rows)
        dtype_dict = {
            'work_id': 'Int64',
            'word_count': 'Int64',
            'hits': 'Int64',
            'kudos': 'Int64',
            'bookmarks': 'Int64',
            'comments': 'Int64',
            'fandom': 'category',  # Categorical is much faster than string
            'top_emotion': 'category',  # Categorical is much faster than string
            'sent_compound': 'float32',
            'sent_pos': 'float32',
            'sent_neg': 'float32',
            'sent_subjectivity': 'float32'
        }

        # Add the emo_ columns to dtype (all are float32)
        for emo in ['fear', 'anger', 'trust', 'surprise', 'sadness', 'disgust', 'joy', 'anticipation']:
            dtype_dict[f'emo_{emo}'] = 'float32'

        # 1. Load the Sentiment File
        df = pd.read_csv(
            file_path,
            parse_dates=['last_updated'],
            dtype=dtype_dict,
            engine='c'  # Faster parser
        )

        # 2. Load NSFW IDs
        if os.path.exists(nsfw_file_path):
            nsfw_ids = pd.read_csv(nsfw_file_path, usecols=['work_id'])['work_id'].unique()
            df['is_nsfw'] = df['work_id'].isin(nsfw_ids)
        else:
            df['is_nsfw'] = False

        # 3. Windows Date Safety
        safe_floor = pd.Timestamp(2000, 1, 1)
        df['last_updated'] = df['last_updated'].fillna(safe_floor)
        df['last_updated'] = df['last_updated'].clip(lower=safe_floor)

        # 4. Fandom Choices
        fandom_counts = df['fandom'].value_counts()
        fandom_choices = {f: f"{f} ({count:,} works)" for f, count in fandom_counts.items()}

        min_date = safe_floor.date()
        max_date = df['last_updated'].max().date()

        return df, fandom_choices, min_date, max_date

    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), {}, date(2000, 1, 1), date.today()
