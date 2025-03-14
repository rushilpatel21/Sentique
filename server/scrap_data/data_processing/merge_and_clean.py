"""
merge_and_clean_debug_updated.py

This script finds all CSV files in two locations:
  1. Directly in the uber_data folder (for BBC and Play Store CSVs)
  2. In the uber_data/twitter_data folder (for Twitter CSVs)

It then determines the appropriate parser based on the filename:
  - If the filename contains "bbc" or "uber_bbc" → BBC parser.
  - If it contains "playstore" or "uber_reviews_playstore" → Play Store parser.
  - Otherwise, it's assumed to be a Twitter CSV.

The script merges all data into a single DataFrame and saves it as uber_merged.csv.
Debug print statements help verify that each file is discovered and loaded.
"""

import os
import pandas as pd

# Define base folders
UBER_DATA_FOLDER = "../uber_data"
TWITTER_DATA_FOLDER = os.path.join(UBER_DATA_FOLDER, "twitter_data")
OUTPUT_FILE = os.path.join(UBER_DATA_FOLDER, "uber_merged.csv")



def load_bbc_csv(file_path: str) -> pd.DataFrame:
    """Load and transform the BBC CSV (news-related)."""
    df = pd.read_csv(file_path)
    df.rename(columns={
        "Publication Date": "date",
        "Content Snippet": "review",
        "Article Title": "username"
    }, inplace=True)
    
    # Replace missing or empty values in 'date' with "NotApplicableToken"
    df["date"] = df["date"].apply(lambda x: x if pd.notna(x) and str(x).strip() != "" else "NotApplicableToken")
    df["source"] = "bbc"
    
    # Keep only the necessary columns.
    df = df[["date", "review", "username", "source"]]
    return df



def load_playstore_csv(file_path: str) -> pd.DataFrame:
    """Load and transform the Play Store CSV."""
    df = pd.read_csv(file_path)
    df.rename(columns={
        "at": "date",
        "content": "review",
        "userName": "username"
    }, inplace=True)
    df["source"] = "playstore"
    df = df[["date", "review", "username", "source"]]
    return df


def load_twitter_csv(file_path: str) -> pd.DataFrame:
    """Load and transform Twitter CSVs."""
    df = pd.read_csv(file_path)
    rename_map = {}

    if "timestamp" in df.columns:
        rename_map["timestamp"] = "date"
    if "text" in df.columns:
        rename_map["text"] = "review"
    if "user_display_name" in df.columns:
        rename_map["user_display_name"] = "username"

    df.rename(columns=rename_map, inplace=True)
    for col in ["date", "review", "username"]:
        if col not in df.columns:
            df[col] = ""
    df["source"] = "twitter"
    df = df[["date", "review", "username", "source"]]
    return df



def get_parser_for_file(filename: str):
    """
    Decide which parser to use based on the filename.
    
    - If filename contains "uber_bbc" or "bbc" → BBC CSV
    - If filename contains "uber_reviews_playstore" or "playstore" → Play Store CSV
    - Otherwise, assume Twitter CSV
    """
    lower_name = filename.lower()
    if "uber_bbc" in lower_name or "bbc" in lower_name:
        return load_bbc_csv
    elif "uber_reviews_playstore" in lower_name or "playstore" in lower_name:
        return load_playstore_csv
    else:
        return load_twitter_csv

def get_all_csv_files():
    """
    Retrieve all CSV files from:
      - The base uber_data folder (for BBC and Play Store files)
      - The uber_data/twitter_data folder (for Twitter files)
    Returns a list of tuples: (filename, folder_path)
    """
    files = []
    # Files directly in uber_data
    for f in os.listdir(UBER_DATA_FOLDER):
        if f.endswith(".csv"):
            files.append((f, UBER_DATA_FOLDER))
    # Files in uber_data/twitter_data (if the folder exists)
    if os.path.isdir(TWITTER_DATA_FOLDER):
        for f in os.listdir(TWITTER_DATA_FOLDER):
            if f.endswith(".csv"):
                files.append((f, TWITTER_DATA_FOLDER))
    return files

def merge_all_csvs():
    """Merge all CSV files into a single DataFrame (without cleaning)."""
    csv_file_list = get_all_csv_files()
    for fname, folder in csv_file_list:
        print(f"  {os.path.join(folder, fname)}")
    
    if not csv_file_list:
        return
    
    all_dfs = []
    for csv_file, folder in csv_file_list:
        full_path = os.path.join(folder, csv_file)
        parser_func = get_parser_for_file(csv_file)
        print(f"\nProcessing file: {csv_file} -> using parser: {parser_func.__name__}")
        try:
            df = parser_func(full_path)
            print(f"   Rows loaded from {csv_file}: {len(df)}")
            all_dfs.append(df)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    if not all_dfs:
        print("No data loaded from any CSV files. Check filenames and contents.")
        return
    
    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal rows in merged DataFrame (no cleaning): {len(merged_df)}")
    merged_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nMerged CSV saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_all_csvs()
