import asyncio
import aiohttp
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse

# -------------------------------------------------------------------
# DISCLAIMER:
# This script is provided solely for educational purposes. It
# demonstrates how asynchronous scraping and sentiment analysis
# can be implemented for personal projects. This example uses Nitter
# as a proxy for Twitter (X) to avoid issues with JavaScript rendering.
# Please ensure that you comply with Nitter’s and Twitter’s terms
# of service before running this script. Do NOT use this for any
# commercial purposes.
# -------------------------------------------------------------------

# Configuration for the website to scrape.
# Here we use Nitter as a proxy for Twitter.
websites = [
    {
        "name": "Twitter",
        # The URL template for searching tweets on Nitter.
        # (Note: Nitter’s HTML structure may change over time.)
        "url": "https://nitter.net/search?f=tweets&q={company}",
        "pages": 3,  # Maximum number of pages to crawl.
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; TwitterScraper/1.0; +https://github.com/yourusername)"
        }
    }
]

async def fetch(session: aiohttp.ClientSession, url: str, headers: dict = None) -> str:
    """Fetch the content of the given URL using aiohttp."""
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()  # Raise exception for HTTP errors.
        return await response.text()

def analyze_sentiment(text: str) -> float:
    """Analyze and return the sentiment polarity of the given text."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def parse_search_results(website_name: str, html: str) -> (list, str):
    """
    Parse the HTML search results and extract tweet text and link pairs.
    Also extracts the "next" page URL (if available) for pagination.
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    if website_name == "Twitter":
        # In Nitter’s search results, each tweet is usually contained
        # in an element with the class "timeline-item". We look for the
        # tweet link (which typically points to the tweet details page)
        # and for a container holding the tweet content.
        for item in soup.find_all("div", class_="timeline-item"):
            # The tweet link is in an <a> tag whose href starts with "/"
            # and typically contains "status" in it.
            tweet_link_tag = item.find("a", href=True)
            if tweet_link_tag and "status" in tweet_link_tag["href"]:
                link = tweet_link_tag["href"]
                # Construct the full URL using Nitter's domain.
                full_link = "https://nitter.net" + link
                # Attempt to extract tweet text.
                content_div = item.find("div", class_="tweet-content")
                tweet_text = content_div.get_text(" ", strip=True) if content_div else ""
                if tweet_text:
                    results.append((tweet_text, full_link))

        # Look for a "Next" page link.
        next_link = None
        next_button = soup.find("a", string="Next")
        if next_button and next_button.get("href"):
            next_link = "https://nitter.net" + next_button["href"]
        return results, next_link

    # If additional websites are added, include additional parsing logic here.
    return results, None

async def fetch_article_details(session: aiohttp.ClientSession, url: str, website_name: str) -> dict:
    """
    Given a tweet (or post) URL, fetch its content and try to extract details:
      - Detailed tweet text (from the tweet-content container)
      - Publication date (if available)
      - Full content (if there is more text on the details page)
    """
    details = {
        "url": url,
        "detail_title": None,
        "publication_date": None,
        "content": ""
    }
    try:
        # Use a basic header; some sites (Nitter) require a proper User-Agent.
        html = await fetch(session, url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        details["error"] = str(e)
        return details

    soup = BeautifulSoup(html, 'html.parser')

    # Extract the detailed tweet text.
    content_div = soup.find("div", class_="tweet-content")
    if content_div:
        content = content_div.get_text(" ", strip=True)
        details["content"] = content
        details["detail_title"] = content  # Use the tweet text as the title.

    # Extract publication date if available.
    # Nitter tweet pages may include a <time> tag with a datetime attribute.
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        details["publication_date"] = time_tag["datetime"]

    return details

async def get_sentiment_for_website(session: aiohttp.ClientSession, website: dict, company: str) -> dict:
    """
    For a given website (here: Twitter via Nitter), fetch search result pages
    (with pagination), extract tweet details, and combine the text for sentiment analysis.
    """
    all_article_text = ""
    all_details = []
    # Start with the initial search URL.
    url = website["url"].format(company=company)
    headers = website.get("headers", {"User-Agent": "Mozilla/5.0"})

    for page in range(website.get("pages", 1)):
        try:
            print(f"Fetching {website['name']} page {page+1} for '{company}'...")
            print(f"URL: {url}")
            html = await fetch(session, url, headers=headers)
            search_results, next_link = parse_search_results(website["name"], html)
            if not search_results:
                print("No search results found; exiting pagination loop.")
                break

            # Fetch details for each tweet concurrently.
            tasks = []
            for tweet_text, link in search_results:
                tasks.append(fetch_article_details(session, link, website["name"]))
            articles_details = await asyncio.gather(*tasks)

            for art in articles_details:
                if art.get("content"):
                    all_article_text += " " + art["content"]
                all_details.append(art)

            # If a "next" link is available, update the URL; otherwise, exit.
            if not next_link:
                print("No next page link found; ending pagination.")
                break
            url = next_link

            # Sleep briefly to avoid overloading the site.
            await asyncio.sleep(1)

        except Exception as e:
            return {"website": website["name"], "sentiment": None, "error": str(e)}

    sentiment = analyze_sentiment(all_article_text) if all_article_text.strip() else None
    return {"website": website["name"], "sentiment": sentiment, "articles": all_details}

async def get_company_sentiment(company: str) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [get_sentiment_for_website(session, website, company) for website in websites]
        results = await asyncio.gather(*tasks)
        return results

def main():
    parser = argparse.ArgumentParser(description="Company Sentiment Analyzer (Twitter Scraper via Nitter)")
    parser.add_argument("--company", type=str, default="Netflix", help="Company name to analyze")
    args = parser.parse_args()
    company = args.company

    results = asyncio.run(get_company_sentiment(company))
    for result in results:
        website = result.get("website", "Unknown")
        if result.get("error"):
            print(f"{website} - Error: {result['error']}")
        else:
            print(f"\n{website} - Overall Sentiment Score: {result['sentiment']}")
            print("Tweets:")
            for idx, art in enumerate(result.get("articles", []), 1):
                print(f"  {idx}. Tweet: {art.get('detail_title', 'N/A')}")
                print(f"     URL: {art.get('url', 'N/A')}")
                pub_date = art.get("publication_date")
                if pub_date:
                    print(f"     Publication Date: {pub_date}")
                content = art.get("content", "")
                snippet = content[:300] + ("..." if len(content) > 300 else "")
                print(f"     Content snippet: {snippet}")
                print("-" * 50)
            print("=" * 80)

if __name__ == "__main__":
    main()
