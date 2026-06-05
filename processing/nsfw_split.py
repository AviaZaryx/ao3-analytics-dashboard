import pandas as pd
import os

# --- SETTINGS ---
INPUT_FILE = r'D:\Downloads\DataVisProj2\data\cleaned_ao3_data.csv'
NSFW_DIR = r'D:\Downloads\DataVisProj2\data\nsfw'
SFW_DIR = r'D:\Downloads\DataVisProj2\data\sfw'

# Define NSFW Keywords for the Additional Tags column
# I've added common AO3 'smut' lingo like PWP (Porn Without Plot) and Lemon
NSFW_KEYWORDS = [
    'smut', 'porn', 'sex', 'pwp', 'erotica', 'lemon', 'nsfw', 'kink',
    'knotting', 'clothed sex', 'oral sex', 'anal sex', 'rimming',
    'rough sex', 'masturbation', 'handjob', 'fingering', 'blowjob',
    'creampie', 'cum', 'bondage', 'bdsm', 'threesome', 'orgasm'
]


def split_data():
    # 1. Create directories if they don't exist
    for folder in [NSFW_DIR, SFW_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

    # 2. Load the cleaned data
    print("Loading cleaned data...")
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # Ensure text columns are strings to avoid errors during search
    df['additional_tags'] = df['additional_tags'].astype(str).str.lower()
    df['rating'] = df['rating'].astype(str)
    df['archive_warning'] = df['archive_warning'].astype(str)

    # 3. DEFINE NSFW CRITERIA

    # A: Rating Check (Mature or Explicit)
    mask_rating = df['rating'].isin(['Mature', 'Explicit'])

    # B: Archive Warning Check (Rape/Non-Con or Underage)
    mask_warning = df['archive_warning'].str.contains('Rape/Non-Con|Underage', case=False, na=False)

    # C: Additional Tags Check (Keyword Search)
    # This joins all keywords into a regex pattern: "smut|porn|sex|..."
    tag_pattern = '|'.join(NSFW_KEYWORDS)
    mask_tags = df['additional_tags'].str.contains(tag_pattern, case=False, na=False)

    # 4. COMBINE AND SPLIT
    # If ANY of the conditions are true, it is NSFW
    is_nsfw = mask_rating | mask_warning | mask_tags

    df_nsfw = df[is_nsfw].copy()
    df_sfw = df[~is_nsfw].copy()

    # 5. SAVE FILES
    nsfw_path = os.path.join(NSFW_DIR, 'nsfw_works.csv')
    sfw_path = os.path.join(SFW_DIR, 'sfw_works.csv')

    print(f"Saving {len(df_nsfw)} NSFW works...")
    df_nsfw.to_csv(nsfw_path, index=False)

    print(f"Saving {len(df_sfw)} SFW works...")
    df_sfw.to_csv(sfw_path, index=False)

    # 6. SUMMARY REPORT
    print("\n" + "=" * 30)
    print("SPLIT COMPLETE")
    print("=" * 30)
    print(f"Total Works Processed: {len(df)}")
    print(f"NSFW Works:            {len(df_nsfw)} ({len(df_nsfw) / len(df):.1%})")
    print(f"SFW Works:             {len(df_sfw)} ({len(df_sfw) / len(df):.1%})")
    print("=" * 30)


if __name__ == "__main__":
    split_data()