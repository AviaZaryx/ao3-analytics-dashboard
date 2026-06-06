import pandas as pd
import re
import unicodedata

# --- CONFIGURATION ---
INPUT_FILE = r'D:\Downloads\DataVisProj2\data\combined_all_works.csv'
OUTPUT_FILE = r'D:\Downloads\DataVisProj2\data\cleaned_ao3_data.csv'

# Acronyms that should remain uppercase
ACRONYMS = {'MCU', 'AU', 'OOC', 'HEA', 'POV', 'RPF', 'DCU', 'DCEU', 'BNHA', 'MHA', 'TWD'}


# --- 1. SMART UTILITIES ---

def normalize_text(text):
    if pd.isna(text) or str(text).lower() == 'none':
        return "None"
    text = unicodedata.normalize('NFKD', str(text))
    return text.strip()


def smart_title_case(text):
    words = text.split()
    processed_words = []
    for word in words:
        clean_word = re.sub(r'\W+', '', word).upper()
        if clean_word in ACRONYMS:
            processed_words.append(word.upper())
        elif not word.islower() and not word.isupper():
            processed_words.append(word)
        else:
            processed_words.append(word.capitalize())
    return " ".join(processed_words)


def canonical_fandom(fandom):
    f = normalize_text(fandom)
    if f == "None": return f
    if '|' in f:
        f = f.split('|')[-1].strip()
    f = re.sub(r'\s*\([^)]*\)', '', f)
    f = re.sub(r'\s*[-–—]\s*All Media Types', '', f, flags=re.IGNORECASE)
    f = re.sub(r'\s*[-–—]\s*Ambiguous Fandom', '', f, flags=re.IGNORECASE)
    return smart_title_case(f.strip())


def canonical_tag(tag):
    t = normalize_text(tag)
    if t == "None": return t
    t = re.sub(r'[!?.]+$', '', t)
    return smart_title_case(t)


def process_tag_list(tag_str):
    if pd.isna(tag_str) or str(tag_str).lower() == 'none':
        return "None"
    tags = [t.strip() for t in str(tag_str).split(',')]
    seen = set()
    cleaned_ordered = []
    for t in tags:
        c = canonical_tag(t)
        if c not in seen and c != "None":
            cleaned_ordered.append(c)
            seen.add(c)
    return ", ".join(cleaned_ordered)


def clean_chapters(value):
    if pd.isna(value) or str(value).strip() == "":
        return 1
    val_str = str(value).split('/')[0]
    nums = re.findall(r'\d+', val_str)
    return int(nums[0]) if nums else 1


# --- 2. MAIN CLEANING LOGIC ---
def run_cleaning():
    print("Reading file...")
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Initial rows: {len(df)}")
    df = df.drop_duplicates(subset=['work_id'], keep='last')

    print("Collapsing Fandoms...")
    unique_fandoms = df['fandom'].unique()
    fandom_map = {f: canonical_fandom(f) for f in unique_fandoms}
    df['fandom'] = df['fandom'].map(fandom_map)

    print("Cleaning Tags...")
    df['additional_tags'] = df['additional_tags'].apply(process_tag_list)

    print("Cleaning numeric strings and fixing word_count type...")
    numeric_cols = ['hits', 'kudos', 'bookmarks', 'comments', 'word_count']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        df[col] = df[col].fillna(0).astype('int64')

    print("Processing chapter formats...")
    df['chapters'] = df['chapters'].apply(clean_chapters).astype('int64')

    print("Converting dates and creating date_numeric...")
    df['last_updated'] = pd.to_datetime(df['last_updated'], dayfirst=True, errors='coerce')
    df['date_numeric'] = df['last_updated'].dt.strftime('%Y%m%d').fillna('0').astype('int64')

    print("Cleaning text placeholders...")
    text_cols = ['title', 'authors', 'relationships', 'characters', 'summary', 'series', 'series_urls', 'series_info']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("None")

    print(f"Saving cleaned data to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print("\nDONE!")
    print(f"Final Row Count: {len(df)}")
    print(f"Unique Fandoms: {df['fandom'].nunique()}")


if __name__ == "__main__":
    run_cleaning()