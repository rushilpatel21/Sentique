import time
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_reddit_comments(url, scrolls=5):
    """
    Launches a Chromium browser (non-headless so you can observe if needed),
    navigates to the Reddit post URL, scrolls to load more comments, and then 
    extracts the text of each comment using BeautifulSoup.
    """
    with sync_playwright() as p:
        # Launch Chromium (set headless=True if you don't want a window)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"Navigating to {url} ...")
        page.goto(url)
        
        # Wait for the page to load
        time.sleep(5)
        
        # Scroll down to load more comments
        for _ in range(scrolls):
            page.mouse.wheel(0, 1000)
            time.sleep(3)
        
        # Get the fully loaded page content
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract comments by looking for divs with data-test-id="comment"
        comment_divs = soup.find_all("div", {"data-test-id": "comment"})
        comments = []
        for div in comment_divs:
            text = div.get_text(separator=" ", strip=True)
            if text:
                comments.append(text)
        
        print(f"Extracted {len(comments)} comments.")
        browser.close()
        return comments

def main():
    # Example Reddit post URL (update this URL as needed)
    url = "https://www.reddit.com/r/LoveIsBlindOnNetflix/comments/ytff4g/current_public_opinion_on_zanab_and_cole/"
    comments = extract_reddit_comments(url, scrolls=5)
    
    # Display a summary of the extracted comments
    for idx, comment in enumerate(comments, start=1):
        print("="*80)
        print(f"Comment {idx}:")
        print(comment)
    
    # Save the comments to a CSV file
    df = pd.DataFrame(comments, columns=["Comment"])
    df.to_csv("reddit_comments.csv", index=False)
    print(f"Saved {len(df)} comments to reddit_comments.csv")

if __name__ == "__main__":
    main()
