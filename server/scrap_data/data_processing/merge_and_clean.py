"""
merge_and_clean_debug.py

This script finds all CSV files in two locations:
  1. Directly in the uber_data folder (for BBC and Play Store CSVs)
  2. In the uber_data/twitter_data folder (for Twitter CSVs)

It determines the appropriate parser based on the filename:
  - If the filename contains "uber_bbc" or "bbc" → BBC parser.
  - If it contains "uber_reviews_playstore" or "playstore" → Play Store parser.
  - Otherwise, it's assumed to be a Twitter CSV.

Additionally, it cleans and normalizes the review text by:
  - Converting text to lowercase
  - Removing HTML tags, URLs, and non-alphanumeric characters (except spaces)
  - Normalizing whitespace
  - Optionally removing numbers 

The script merges all data into a single DataFrame and saves it as uber_merged.csv.
Debug print statements help verify that each file is discovered and loaded.
"""

import os    # Used for file and directory operations, such as listing files in a directory and constructing file paths.
import pandas as pd   
import re    # Provides regular expression functions, which are employed in cleaning and normalizing text (e.g., removing HTML tags, URLs, and special characters).


# Define base folders
UBER_DATA_FOLDER = "../uber_data"
TWITTER_DATA_FOLDER = os.path.join(UBER_DATA_FOLDER, "twitter_data")
OUTPUT_FILE = os.path.join(UBER_DATA_FOLDER, "uber_merged.csv")

def clean_text(text):
    """
    Clean and normalize review text.
    Steps:
      - Lowercase
      - Remove HTML tags
      - Remove URLs
      - Remove non-alphanumeric characters (punctuation, emojis, etc.)
      - Normalize whitespace
    """
    if not isinstance(text, str):
        text = str(text)
    # Convert to lowercase
    text = text.lower()
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove non-alphanumeric characters (retain spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_bbc_csv(file_path: str) -> pd.DataFrame:
    """Load and transform the BBC CSV (news-related)."""
    print(f"  -> Loading BBC CSV: {file_path}")
    df = pd.read_csv(file_path)
    df.rename(columns={
        "Publication Date": "date",
        "Content Snippet": "review",
        "Article Title": "username"  # If you want to capture Article Title as username or leave it empty
    }, inplace=True)
    
    # Replace missing or empty values in 'date' with "NotApplicableToken"
    df["date"] = df["date"].apply(lambda x: x if pd.notna(x) and str(x).strip() != "" else "NotApplicableToken")
    
    # Clean the review text
    df["review"] = df["review"].apply(clean_text)
    
    df["source"] = "bbc"
    
    # Keep only the necessary columns.
    df = df[["date", "review", "username", "source"]]
    return df

def load_playstore_csv(file_path: str) -> pd.DataFrame:
    """Load and transform the Play Store CSV."""
    print(f"  -> Loading Play Store CSV: {file_path}")
    df = pd.read_csv(file_path)
    df.rename(columns={
        "at": "date",
        "content": "review",
        "userName": "username"
    }, inplace=True)
    
    # Clean the review text
    df["review"] = df["review"].apply(clean_text)
    
    df["source"] = "playstore"
    df = df[["date", "review", "username", "source"]]
    return df

def load_twitter_csv(file_path: str) -> pd.DataFrame:
    """Load and transform Twitter CSVs."""
    print(f"  -> Loading Twitter CSV: {file_path}")
    df = pd.read_csv(file_path)
    rename_map = {}
    if "timestamp" in df.columns:
        rename_map["timestamp"] = "date"
    if "text" in df.columns:
        rename_map["text"] = "review"
    if "user_display_name" in df.columns:
        rename_map["user_display_name"] = "username"
    df.rename(columns=rename_map, inplace=True)
    
    # Ensure required columns exist (fill missing ones with empty string)
    for col in ["date", "review", "username"]:
        if col not in df.columns:
            df[col] = ""
    
    # Clean the review text
    df["review"] = df["review"].apply(clean_text)
    
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
        print(f"  File '{filename}' identified as BBC.")
        return load_bbc_csv
    elif "uber_reviews_playstore" in lower_name or "playstore" in lower_name:
        print(f"  File '{filename}' identified as Play Store.")
        return load_playstore_csv
    else:
        print(f"  File '{filename}' identified as Twitter.")
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
    """Merge all CSV files into a single DataFrame (without additional cleaning)."""
    csv_file_list = get_all_csv_files()
    print("Discovered CSV files:")
    for fname, folder in csv_file_list:
        print(f"  {os.path.join(folder, fname)}")
    
    if not csv_file_list:
        print("No CSV files found. Please check your folders and filenames.")
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
    print(f"\nTotal rows in merged DataFrame (no extra cleaning): {len(merged_df)}")
    merged_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nMerged CSV saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_all_csvs()
