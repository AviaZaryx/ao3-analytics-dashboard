import pandas as pd
import os
import numpy as np

# --- SETTINGS ---
FILE_PATH = r'D:\Downloads\DataVisProj2\data\cleaned_ao3_data.csv'


def perform_data_check(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return

    print(f"{'=' * 70}")
    print(f"COMPREHENSIVE DATA CHECK REPORT: {os.path.basename(filepath)}")
    print(f"{'=' * 70}")

    # 1. Load the data
    df = pd.read_csv(filepath, low_memory=False)

    # 2. Basic Dimensions
    print(f"\n[1] DIMENSIONS:")
    print(f"Total Rows:    {df.shape[0]}")
    print(f"Total Columns: {df.shape[1]}")

    # 3. Data Types and Memory (More detailed check for cleaned types)
    print(f"\n[2] COLUMN INFO & VERIFIED TYPES:")
    print(df.info())

    print(f"\n[2a] VERIFYING KEY DTYPES (Int64, Datetime, and Chapters):")
    expected_int_cols = ['work_id', 'word_count', 'comments', 'kudos', 'bookmarks', 'hits', 'date_numeric', 'chapters']
    expected_datetime_cols = ['last_updated']

    for col in expected_int_cols:
        actual_dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(actual_dtype) or str(actual_dtype) == 'Int64':
            print(f"  '{col}': OK - Expected Int64/int, got {actual_dtype}")
        else:
            print(f"  '{col}': WARNING - Expected Int64/int, got {actual_dtype}")

    for col in expected_datetime_cols:
        actual_dtype = df[col].dtype
        if pd.api.types.is_datetime64_any_dtype(actual_dtype):
            print(f"  '{col}': OK - Expected datetime, got {actual_dtype}")
        else:
            print(f"  '{col}': WARNING - Expected datetime, got {actual_dtype}")

    print(f"\n[2b] DATE RANGE (last_updated):")
    if pd.api.types.is_datetime64_any_dtype(df['last_updated']):
        print(f"  Min Date: {df['last_updated'].min()}")
        print(f"  Max Date: {df['last_updated'].max()}")
        print(f"  Number of missing dates (NaT): {df['last_updated'].isnull().sum()}")
    else:
        print("  'last_updated' is not a datetime column, cannot display date range.")

    # 4. Missing Values & 'None' Counts (Updated for text replacement)
    print(f"\n[3] MISSING VALUES & 'None' COUNTS (Top 10):")
    null_counts = df.isnull().sum()

    for col in df.columns:
        if df[col].dtype == 'object':
            none_count = (df[col] == 'None').sum()
            if none_count > 0:
                null_counts[col] = null_counts.get(col, 0) + none_count

    if null_counts.sum() == 0:
        print("No missing values (NaN) or 'None' placeholders found!")
    else:
        significant_nulls = null_counts[null_counts > 0].sort_values(ascending=False)
        print(significant_nulls.head(10))

    # 5. Duplicate Rows
    print(f"\n[4] DUPLICATES:")
    duplicate_count = df.duplicated().sum()
    print(f"Number of duplicate rows: {duplicate_count} (Expected: 0 after cleaning)")
    if duplicate_count > 0:
        print(
            "  WARNING: Duplicates found! Cleaning might not have been fully effective or new duplicates were introduced.")

    # 6. Numeric Summary (Hits, Bookmarks, etc.)
    print(f"\n[5] NUMERIC SUMMARY:")
    print(df.describe())

    # 7. Categorical Column Insights
    print(f"\n[6] CATEGORICAL COLUMN INSIGHTS:")
    categorical_cols = ['rating', 'fandom', 'category', 'language', 'completion_status']
    for col in categorical_cols:
        print(f"\n  -- '{col}' --")
        print(f"  Unique values: {df[col].nunique()}")
        print("  Top 5 values:")
        print(df[col].value_counts().head(5))

    # 8. Numeric Anomalies
    print(f"\n[7] NUMERIC ANOMALIES (Counts of 0 or extreme values):")
    zero_cols = ['word_count', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits']
    for col in zero_cols:
        zero_count = (df[col].fillna(-1) == 0).sum()
        if zero_count > 0:
            print(f"  '{col}': {zero_count} entries have a value of 0 (e.g., 0-word stories, 0-hit stories).")

    if 'chapters' in df.columns:
        high_chapters = df[df['chapters'] > 100].shape[0]
        if high_chapters > 0:
            print(
                f"  'chapters': {high_chapters} entries have >100 chapters. Consider checking (max: {df['chapters'].max()}).")

    # 9. Sample of Data
    print(f"\n[8] DATA PREVIEW (First 5 rows):")
    print(df.head())

    print(f"\n{'=' * 70}")
    print("COMPREHENSIVE DATA CHECK COMPLETE!")


if __name__ == "__main__":
    perform_data_check(FILE_PATH)