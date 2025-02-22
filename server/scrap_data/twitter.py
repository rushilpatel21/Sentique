import time
import pandas as pd
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_x_search(output_csv="x_search_results.csv", scrolls=15):
    """
    Scrape textual tweets from X.com using a custom query:
    "Oyo (#Oyo) lang:en -filter:links", which returns English tweets for #Oyo
    without links.
    
    Parameters:
      - output_csv: Filename for saving the results.
      - scrolls: Number of scroll actions to load more tweets.
    """
    # Hardcode the query as specified.
    query = "Oyo (#Oyo) lang:en -filter:links"
    encoded_query = quote(query)
    # You can adjust sort_type if desired; here we use "top" for popular/trending tweets.
    search_url = f"https://x.com/search?q={encoded_query}&f=top"
    print(f"Navigating to {search_url} ...")
    
    # Replace with the path to your Chromium user data folder containing your logged-in session.
    user_data_dir = "C:/Users/Lenovo/AppData/Local/Chromium/User Data"
    
    with sync_playwright() as p:
        # Launch a persistent context to reuse the logged-in session.
        context = p.chromium.launch_persistent_context(user_data_dir=user_data_dir, headless=False)
        page = context.new_page()
        page.goto(search_url)
        
        # Allow time for the page to load and tweets to render.
        time.sleep(5)
        
        # Scroll to load additional tweets.
        for i in range(scrolls):
            page.mouse.wheel(0, 1000)
            time.sleep(3)
        
        # Get the page content and parse with BeautifulSoup.
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        tweets = []
        for article in soup.find_all("article"):
            # Skip tweets that have media elements (if desired).
            if article.find(attrs={"data-testid": "tweetPhoto"}) or article.find(attrs={"data-testid": "videoPlayer"}):
                continue
            tweet_text = article.get_text(separator=" ", strip=True)
            if tweet_text:
                tweets.append(tweet_text)
        
        print(f"Extracted {len(tweets)} textual tweets from the page.")
        context.close()
    
    # Save results to a CSV file.
    df = pd.DataFrame(tweets, columns=["Tweet"])
    df.to_csv(output_csv, index=False)
    print(tweets)
    print(f"Saved {len(df)} tweets to {output_csv}")

if __name__ == "__main__":
    scrape_x_search()
