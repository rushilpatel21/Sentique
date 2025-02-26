import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse

# List of websites with URL templates and pagination limits.
websites = [
    {
        "name": "BBC",
        "url": "https://www.bbc.co.uk/search?q={company}&d=SEARCH_PS&page={page}",
        "pages": 20
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
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        details["detail_title"] = og_title["content"]
    elif soup.title:
        details["detail_title"] = soup.title.get_text(strip=True)
    
    # Extract publication date if available:
    pub_date = None
    for attr in [("property", "article:published_time"), ("name", "pubdate"), ("name", "date")]:
        tag = soup.find("meta", attrs={attr[0]: attr[1]})
        if tag and tag.get("content"):
            pub_date = tag["content"]
            break
    details["publication_date"] = pub_date
    
    # Extract main article content.
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
                # No results found; break out.
                break
            # Fetch article details concurrently.
            tasks = [fetch_article_details(session, link, website["name"]) for title, link in search_results]
            articles_details = await asyncio.gather(*tasks)
            for art in articles_details:
                if art.get("content"):
                    all_article_text += " " + art["content"]
                all_details.append(art)
            await asyncio.sleep(1)
        except Exception as e:
            return {"website": website["name"], "sentiment": None, "error": str(e), "articles": []}
    sentiment = analyze_sentiment(all_article_text) if all_article_text.strip() else None
    return {"website": website["name"], "sentiment": sentiment, "articles": all_details}

async def get_company_sentiment(company: str) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = [get_sentiment_for_website(session, website, company) for website in websites]
        results = await asyncio.gather(*tasks)
        return results

def write_to_csv(results: list, filename: str = "output.csv"):
    """
    Writes the analysis results to a CSV file.
    Each row represents an article with details and includes the website overall sentiment.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Website", "Overall Sentiment", "Article Title", "URL", "Publication Date", "Content Snippet"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            website_name = result.get("website", "N/A")
            overall_sentiment = result.get("sentiment", "N/A")
            articles = result.get("articles", [])
            if articles:
                for art in articles:
                    snippet = art.get("content", "")[:]
                    writer.writerow({
                        "Website": website_name,
                        "Overall Sentiment": overall_sentiment,
                        "Article Title": art.get("detail_title", "N/A"),
                        "URL": art.get("url", "N/A"),
                        "Publication Date": art.get("publication_date", "N/A"),
                        "Content Snippet": snippet + ("..." if len(art.get('content', "")) > 300 else "")
                    })
            else:
                # If no articles or an error occurred, record the error message.
                error = result.get("error", "No articles found")
                writer.writerow({
                    "Website": website_name,
                    "Overall Sentiment": overall_sentiment,
                    "Article Title": "Error",
                    "URL": "",
                    "Publication Date": "",
                    "Content Snippet": error
                })

def main():
    parser = argparse.ArgumentParser(description="Company Detailed Sentiment Analyzer with CSV Output")
    parser.add_argument("--company", type=str, default="Uber", help="Company name to analyze")
    args = parser.parse_args()
    company = args.company
    print(f"The company name is set to '{company}'")
    results = asyncio.run(get_company_sentiment(company))
    
    # Write results to CSV file.
    write_to_csv(results, filename="uber_bbc.csv")
    print("Results have been written to uber_bbc.csv")

if __name__ == "__main__":
    main()
