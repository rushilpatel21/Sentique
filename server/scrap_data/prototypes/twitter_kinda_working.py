import time
import pandas as pd
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_x_search(query, sort_type="top", output_csv="x_search_results.csv", scrolls=5):
    """
    Scrape tweets from X.com using a persistent browser session.
    
    Parameters:
      - query: The search term (e.g., "Netflix")
      - sort_type: "top" for popular/trending tweets, "live" for recent tweets.
      - output_csv: Filename for saving results.
      - scrolls: Number of times to scroll to load additional tweets.
    """
    # Update the query to filter for English tweets
    query_filter = f"{query} lang:en"
    encoded_query = quote(query_filter)
    # Build the search URL with the sort type parameter
    search_url = f"https://x.com/search?q={encoded_query}&f={sort_type}"
    print(f"Navigating to {search_url} ...")
    
    # Replace with the path to your Chromium user data folder (with logged-in session)
    user_data_dir = "C:/Users/Lenovo/AppData/Local/Chromium/User Data"
    
    with sync_playwright() as p:
        # Launch a persistent context so your login session is reused.
        context = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, headless=False)
        page = context.new_page()
        page.goto(search_url)
        
        # Wait for the page to load and tweets to render
        time.sleep(5)
        
        # Scroll to load additional tweets
        for i in range(scrolls):
            page.mouse.wheel(0, 1000)
            time.sleep(3)
        
        # Get the page content and parse it with BeautifulSoup
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract tweet containers; adjust selectors as needed if X.com layout changes.
        tweets = []
        for article in soup.find_all("article"):
            tweet_text = article.get_text(separator=" ", strip=True)
            if tweet_text:
                tweets.append(tweet_text)
        
        print(f"Extracted {len(tweets)} tweets from the page.")
        context.close()
    
    # Save results to a CSV file
    df = pd.DataFrame(tweets, columns=["Tweet"])
    df.to_csv(output_csv, index=False)
    print(df)
    print(f"Saved {len(df)} tweets to {output_csv}")

if __name__ == "__main__":
    # Hardcoded for Netflix as an example.
    # Change sort_type to "live" for recent tweets or "top" for popular/trending.
    scrape_x_search("Netflix", sort_type="top")
