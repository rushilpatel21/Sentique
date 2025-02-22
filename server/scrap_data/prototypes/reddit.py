import asyncio
import aiohttp
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse

# -------------------------------------------------------------------
# DISCLAIMER:
# This script is provided solely for educational purposes. It
# demonstrates how asynchronous scraping and sentiment analysis
# can be implemented for personal projects. Please ensure that
# you comply with Reddit's terms of service and robots.txt before
# running this script. Do NOT use this for any commercial purposes.
# -------------------------------------------------------------------

# Configuration for the website to scrape (using old.reddit.com)
websites = [
    {
        "name": "Reddit",
        # The URL template for searching posts on old.reddit.com.
        # Note: Old Reddit shows search results in a way that allows
        # us to follow the "next" button for pagination.
        "url": "https://old.reddit.com/search/?q={company}",
        "pages": 3,  # Maximum number of pages to crawl.
        # Providing a custom User-Agent is important as Reddit may block
        # requests with the default one.
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; RedditScraper/1.0; +https://github.com/yourusername)"
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
    Parse the HTML search results and extract article (post) title and link pairs.
    Also extracts the "next" page URL (if available) for pagination.
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    if website_name == "Reddit":
        # On old.reddit.com, each search result typically has an <a>
        # tag with the class "search-title".
        for a in soup.find_all("a", class_="search-title"):
            title = a.get_text(strip=True)
            link = a.get("href")
            if title and link:
                results.append((title, link))

        # Find the pagination "next" button.
        next_link = None
        next_button = soup.find("span", class_="next-button")
        if next_button and next_button.find("a"):
            next_link = next_button.find("a")["href"]
        return results, next_link

    # If additional websites are added, include additional parsing logic here.
    return results, None

async def fetch_article_details(session: aiohttp.ClientSession, url: str, website_name: str) -> dict:
    """
    Given an article (or post) URL, fetch its content and try to extract details:
      - Detailed title (from <title>)
      - Publication date (if available)
      - Main article/post text content.
    """
    details = {
        "url": url,
        "detail_title": None,
        "publication_date": None,
        "content": ""
    }
    try:
        # Use a basic header here; some sites (Reddit) require a proper User-Agent.
        html = await fetch(session, url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        details["error"] = str(e)
        return details

    soup = BeautifulSoup(html, 'html.parser')

    # Extract the detailed title from the <title> tag.
    if soup.title:
        details["detail_title"] = soup.title.get_text(strip=True)

    # Try to extract the publication date.
    # Reddit posts might show a <time> tag with a datetime attribute.
    time_tag = soup.find("time")
    if time_tag and time_tag.get("datetime"):
        details["publication_date"] = time_tag["datetime"]

    # Extract the main content.
    # For Reddit self-posts, content is usually found in a <div> with a class like "usertext-body"
    content_div = soup.find("div", class_="expando") or soup.find("div", class_="usertext-body")
    if content_div:
        details["content"] = content_div.get_text(" ", strip=True)
    else:
        # Fallback: collect text from all paragraph tags.
        paragraphs = soup.find_all("p")
        details["content"] = " ".join(p.get_text(strip=True) for p in paragraphs)

    return details

async def get_sentiment_for_website(session: aiohttp.ClientSession, website: dict, company: str) -> dict:
    """
    For a given website (here: Reddit), fetch search result pages (with pagination),
    extract post details, and combine the text for sentiment analysis.
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

            # Fetch details for each search result concurrently.
            tasks = []
            for title, link in search_results:
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
    parser = argparse.ArgumentParser(description="Company Sentiment Analyzer (Reddit Scraper)")
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
            print("Articles:")
            for idx, art in enumerate(result.get("articles", []), 1):
                print(f"  {idx}. Title: {art.get('detail_title', 'N/A')}")
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
