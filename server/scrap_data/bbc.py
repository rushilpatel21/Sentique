import asyncio
import aiohttp
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse

# List of websites with URL templates and pagination limits.
websites = [
    {
        "name": "BBC",
        "url": "https://www.bbc.co.uk/search?q={company}&d=SEARCH_PS&page={page}",
        "pages": 5
    }
]

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

def analyze_sentiment(text: str) -> float:
    blob = TextBlob(text)
    return blob.sentiment.polarity

def parse_search_results(website_name: str, html: str) -> list:
    """
    Extracts article title and link pairs from a search result page.
    Uses simple heuristics based on the website.
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    if website_name == "BBC":
        # BBC: look for <a> tags whose href contains '/news/'
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/news/" in href:
                title = a.get_text(strip=True)
                if title:
                    if not href.startswith("http"):
                        href = "https://www.bbc.co.uk" + href
                    results.append((title, href))
    return results

async def fetch_article_details(session: aiohttp.ClientSession, url: str, website_name: str) -> dict:
    """
    Given an article URL, fetch its content and try to extract details:
      - detailed title (from <title> or meta og:title)
      - publication date (from common meta tags)
      - full article text (from <article> tag if available or fallback to concatenated <p> tags)
    """
    details = {"url": url, "detail_title": None, "publication_date": None, "content": ""}
    try:
        html = await fetch(session, url)
    except Exception as e:
        details["error"] = str(e)
        return details
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract detailed title:
    # Prefer meta tag og:title if available.
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        details["detail_title"] = og_title["content"]
    else:
        # Fallback to the <title> tag
        if soup.title:
            details["detail_title"] = soup.title.get_text(strip=True)
    
    # Extract publication date if available:
    # Check common meta names or properties.
    pub_date = None
    for attr in [("property", "article:published_time"), ("name", "pubdate"), ("name", "date")]:
        tag = soup.find("meta", attrs={attr[0]: attr[1]})
        if tag and tag.get("content"):
            pub_date = tag["content"]
            break
    details["publication_date"] = pub_date
    
    # Extract main article content.
    # First try to get text inside an <article> tag.
    article_tag = soup.find("article")
    if article_tag:
        paragraphs = article_tag.find_all("p")
    else:
        paragraphs = soup.find_all("p")
    content = " ".join(p.get_text(strip=True) for p in paragraphs)
    details["content"] = content
    return details

async def get_sentiment_for_website(session: aiohttp.ClientSession, website: dict, company: str) -> dict:
    """
    For a given website, fetch all pages (using pagination if applicable),
    extract search results, then fetch details for each article.
    Combine all article texts for sentiment analysis.
    """
    all_article_text = ""
    all_details = []
    max_pages = website.get("pages", 1)
    for page in range(1, max_pages + 1):
        if "{from_val}" in website["url"]:
            from_val = (page - 1) * 10
            url = website["url"].format(company=company, page=page, from_val=from_val)
        elif "{page}" in website["url"]:
            url = website["url"].format(company=company, page=page)
        else:
            url = website["url"].format(company=company)
        try:
            print(f"Fetching {website['name']} page {page} for {company}...")
            print(url)
            html = await fetch(session, url)
            search_results = parse_search_results(website["name"], html)
            if not search_results:
                # If no results on this page, break out.
                break
            # For each search result, fetch article details concurrently.
            tasks = []
            for title, link in search_results:
                tasks.append(fetch_article_details(session, link, website["name"]))
            articles_details = await asyncio.gather(*tasks)
            for art in articles_details:
                if art.get("content"):
                    all_article_text += " " + art["content"]
                all_details.append(art)
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
    parser = argparse.ArgumentParser(description="Company Detailed Sentiment Analyzer")
    parser.add_argument("--company", type=str, default="Netflix", help="Company name to analyze")
    args = parser.parse_args()
    company = args.company

    results = asyncio.run(get_company_sentiment(company))
    for result in results:
        website = result["website"]
        if result.get("error"):
            print(f"{website} - Error: {result['error']}")
        else:
            print(f"{website} - Overall Sentiment score: {result['sentiment']}")
            print("Articles:")
            for idx, art in enumerate(result.get("articles", []), 1):
                print(f"  {idx}. Title: {art.get('detail_title', 'N/A')}")
                print(f"     URL: {art.get('url', 'N/A')}")
                pub_date = art.get("publication_date")
                if pub_date:
                    print(f"     Publication Date: {pub_date}")
                content = art.get("content", "")
                # Show first 300 characters of content as a snippet.
                snippet = content[:300] + ("..." if len(content) > 300 else "")
                print(f"     Content snippet: {snippet}")
                print("-" * 50)
            print("=" * 80)

if __name__ == "__main__":
    main()