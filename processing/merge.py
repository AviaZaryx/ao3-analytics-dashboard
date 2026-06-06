import pandas as pd
import glob
import os

input_path = r'D:\Downloads\DataVisProj2\data\raw data'
output_path = r'D:\Downloads\DataVisProj2\data\combined_all_works.csv'


def merge_csv_files():
    # 1. Get a list of all CSV files in the source directory
    all_files = glob.glob(os.path.join(input_path, "*.csv"))

    if not all_files:
        print(f"No CSV files found in {input_path}")
        return

    print(f"Found {len(all_files)} files. Starting merge...")

    li = []

    # 2. Loop through each file and read it into a list
    for filename in all_files:
        print(f"Reading: {os.path.basename(filename)}")

        df = pd.read_csv(filename, index_col=None, header=0, low_memory=False, thousands=',')
        li.append(df)

    # 3. Concatenate all dataframes into one
    print("Merging data...")
    combined_df = pd.concat(li, axis=0, ignore_index=True)

    # 4. Save the combined dataframe to the destination
    combined_df.to_csv(output_path, index=False)

    print("-" * 30)
    print(f"Success! Combined file saved to: {output_path}")
    print(f"Total rows: {len(combined_df)}")


if __name__ == "__main__":
    merge_csv_files()