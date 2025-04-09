import argparse
import csv
import json
import logging
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

session = requests.Session()


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    :return: Namespace object with parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Scrape reviews from Trustpilot for a given domain."
    )
    parser.add_argument("domain", help="The domain to scrape reviews for.", type=str)
    parser.add_argument(
        "--stars",
        nargs="*",
        help="Filter reviews by stars. Accept multiple values (e.g., --stars 4 5).",
        type=int,
    )
    parser.add_argument(
        "--date",
        help="Filter reviews by date (e.g., last30days, last3months, last6months).",
        type=str,
    )
    parser.add_argument(
        "--verified",
        action="store_true",
        help="Filter reviews to show only verified reviews.",
    )
    parser.add_argument(
        "--replies",
        action="store_true",
        help="Filter reviews to show only reviews with replies.",
    )
    parser.add_argument(
        "--sort-by",
        help="Sort reviews by a specified field (e.g., 'rating', 'date').",
        type=str,
        default="published_date",
    )
    parser.add_argument(
        "--sort-order",
        choices=["asc", "desc"],
        default="asc",
        help="Sort order: 'asc' for ascending, 'desc' for descending. Default is ascending.",
    )
    parser.add_argument(
        "--output",
        choices=["csv", "json", "both"],
        default="json",
        help="Specify the output format: 'csv' for CSV file, 'json' for JSON file, or 'both' for both formats. Default is 'csv'.",
    )

    return parser.parse_args()


def generate_url(domain: str, page: int, args) -> str:
    """
    Generate the URL for the given domain, page number, and additional filters in a more concise manner.
    :param domain: The domain to get the reviews for.
    :param page: The page number.
    :param args: Parsed command-line arguments containing filters.
    :return: The URL for the given domain and page number with query parameters.
    """
    base_url = f"https://www.trustpilot.com/review/{domain}"
    params = {}

    if args.stars:
        for star in args.stars:
            params[f"stars"] = star
    if args.date:
        params["date"] = args.date
    if args.search:
        params["search"] = args.search
    if args.languages:
        params["languages"] = args.languages
    if args.verified:
        params["verified"] = "true"
    if args.replies:
        params["replies"] = "true"

    if page > 1:
        params["page"] = page

    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{base_url}?{query_string}" if params else base_url


def get_html_with_retry(url: str, retry_enabled: bool) -> BeautifulSoup | None:
    """
    Adds retry capability for failed requests
    """
    if retry_enabled:
        retries = 3
        for attempt in range(retries):
            try:
                return get_html(url)
            except requests.exceptions.RequestException:
                logger.warning(f"Retrying ({attempt + 1}/{retries})...")
                time.sleep(random.randint(1, 3))
    return get_html(url)


def is_allowed_by_robots_txt(url: str, user_agent: str) -> bool:
    """
    Check if the given user agent is allowed to scrape the URL according to robots.txt rules.
    :param url: The base URL of the website to check.
    :param user_agent: The User-Agent string of the scraper.
    :return: True if allowed, False otherwise.
    """
    parser = RobotFileParser()
    parser.set_url(f"{url}/robots.txt")
    parser.read()
    return parser.can_fetch(user_agent, url)


def iso_to_datetime(iso_str: str) -> datetime | None:
    """
    Convert an ISO 8601 formatted string to a datetime object.
    :param iso_str: The ISO 8601 formatted string.
    :return: The datetime object.
    """
    if iso_str:
        # Remove the 'Z' and convert to datetime
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return None


def get_html(url: str) -> BeautifulSoup | None:
    """
    Get the HTML content of the given URL using a persistent session.
    :param url: The URL to get the HTML content from.
    :return: BeautifulSoup object containing the HTML content.
    """
    ua = UserAgent()
    session.headers.update({"User-Agent": ua.random})
    response = session.get(url)

    final_url = response.url
    initial_params = parse_qs(urlparse(url).query)
    final_params = parse_qs(urlparse(final_url).query)
    if len(initial_params) > 1 and initial_params != final_params:
        logger.error(f"Redirected to {final_url}. Unexpected redirection detected.")
        sys.exit(1)

    if response.status_code == 404:
        return None

    if response.status_code == 200:
        html_content = BeautifulSoup(response.content, "lxml")
        return html_content
    response.raise_for_status()


def get_reviews_data(html: BeautifulSoup) -> list[dict]:
    """
    Get the reviews data from the HTML content.
    :param html: BeautifulSoup object containing the HTML content.
    :return: List of dictionaries containing the review data.
    """
    script_tag = html.find("script", {"id": "__NEXT_DATA__"})
    return json.loads(script_tag.string)["props"]["pageProps"]["reviews"]


def parse_review(review: dict) -> dict:
    """
    Parse the review data and extract the relevant information.
    :param review: Dictionary containing the raw review data.
    :return: Dictionary containing the processed review data.
    """
    parsed_review = {
        "id": review.get("id"),
        "filtered": review.get("filtered"),
        "pending": review.get("pending"),
        "text": review.get("text"),
        "rating": review.get("rating"),
        "title": review.get("title"),
        "likes": review.get("likes"),
        "report": review.get("report"),
        "has_unhandled_reports": review.get("hasUnhandledReports"),
        "language": review.get("language"),
        "location": review.get("location"),
        "consumers_review_count_on_same_domain": review.get(
            "consumersReviewCountOnSameDomain"
        ),
        "consumers_review_count_on_same_location": review.get(
            "consumersReviewCountOnSameLocation"
        ),
    }

    # Date information
    dates = review.get("dates", {})
    parsed_review["published_date"] = iso_to_datetime(dates.get("publishedDate"))
    parsed_review["experienced_date"] = iso_to_datetime(dates.get("experiencedDate"))
    parsed_review["updated_date"] = iso_to_datetime(dates.get("updatedDate"))

    # Consumer information
    consumer = review.get("consumer", {})
    parsed_review["display_name"] = consumer.get("displayName")
    parsed_review["image_url"] = consumer.get("imageUrl")
    parsed_review["review_count"] = consumer.get("numberOfReviews")
    parsed_review["country_code"] = consumer.get("countryCode")
    parsed_review["has_image"] = consumer.get("hasImage")
    parsed_review["consumer_verified"] = consumer.get("isVerified")

    # Verification labels
    labels = review.get("labels", {}).get("verification", {})
    parsed_review["review_verified"] = labels.get("isVerified")
    parsed_review["review_verification_level"] = labels.get("verificationLevel")
    parsed_review["review_verification_source"] = labels.get("verificationSource")
    parsed_review["review_verification_date"] = labels.get("createdDateTime")
    parsed_review["review_source_name"] = labels.get("reviewSourceName")
    parsed_review["has_dach_exclusion"] = labels.get("hasDachExclusion")

    # Reply information
    reply = review.get("reply")
    if reply:
        parsed_review["reply_message"] = reply.get("message")
        parsed_review["reply_published_date"] = iso_to_datetime(
            reply.get("publishedDate")
        )
        parsed_review["reply_updated_date"] = iso_to_datetime(reply.get("updatedDate"))
    else:
        parsed_review["reply_message"] = None
        parsed_review["reply_published_date"] = None
        parsed_review["reply_updated_date"] = None

    return parsed_review


def process_reviews(reviews_data: list[dict]) -> list[dict]:
    """
    Process the reviews data and extract the relevant information.
    :param reviews_data: List of dictionaries containing the raw review data.
    :return: List of dictionaries containing the processed review data.
    """
    return [parse_review(review) for review in reviews_data]

def datetime_converter(o: object) -> str:
    """
    Convert a datetime object to a string.
    :param o: The object to convert.
    :return: The string representation of the object.
    """
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(
        "Object of type '{}' is not JSON serializable".format(o.__class__.__name__)
    )


def write_reviews_to_json(reviews: list[dict], filename: str) -> None:
    """
    Write the reviews to a JSON file, converting datetime objects to strings.
    :param reviews: List of dictionaries containing the review details.
    :param filename: The name of the JSON file to write the reviews to.
    """
    # Convert datetime objects to strings
    reviews_converted = []
    for review in reviews:
        review_converted = {
            'review_id': datetime_converter(review['id']) if isinstance(review['id'], datetime) else review['id'],
            'title': review['title'],
            'language': review['language'],
            'date': datetime_converter(review['published_date']) if isinstance(review['published_date'], datetime) else
            review['published_date'],
            'username': review['display_name'],
            'rating': review['rating'],
            'source': 'trustpilot'
        }
        reviews_converted.append(review_converted)
    with open(filename, "w") as file:
        json.dump(reviews_converted, file, indent=4)


def sort_reviews(reviews: list[dict], sort_by: str, sort_order: str) -> list[dict]:
    """
    Sort the reviews by a specified field in ascending or descending order.
    :param reviews: List of dictionaries containing the review details.
    :param sort_by: The field to sort the reviews by.
    :param sort_order: The order to sort the reviews in ('asc' for ascending, 'desc' for descending).
    :return: List of dictionaries containing the sorted review details.
    """
    reverse = sort_order == "desc"
    if sort_by and any(review.get(sort_by) for review in reviews):
        if sort_by in ["published_date", "experienced_date", "updated_date"]:
            return sorted(
                reviews,
                key=lambda x: x.get(sort_by) or datetime.min,
                reverse=reverse,
            )
        else:
            return sorted(reviews, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    return reviews



def save_reviews(reviews: list[dict], domain: str, start_page: int, end_page: int) -> None:
    """Save reviews to a JSON file with a filename indicating the page range."""
    filename = f"reviews_{domain}_pages_{start_page}_to_{end_page}.json"
    write_reviews_to_json(reviews, filename)
    logger.info(f"Saved {len(reviews)} reviews to {filename}")

def handle_pagination_and_lazy_loading(url: str, max_retries: int = 3, timeout: int = 10) -> str | None:
    """
    Handles dynamic content loading and pagination using Selenium with improved error handling
    and resource management.

    Args:
        url: The URL to scrape
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Maximum time to wait for elements (default: 10 seconds)

    Returns:
        str: The page source with dynamically loaded content, or None if failed
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = None
    retry_delay = 2

    try:
        for attempt in range(max_retries):
            try:
                if driver:
                    driver.quit()

                driver = webdriver.Chrome(options=options)
                driver.get(url)

                # Wait for reviews container
                review_container = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'review-list'))
                )

                # Scroll to load all reviews
                last_height = driver.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Wait for new content to load
                    time.sleep(2)

                    # Calculate new scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")

                    # Break if no more content loaded
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Ensure all reviews are loaded
                reviews = driver.find_elements(By.CLASS_NAME, 'review-card')
                logger.info(f"Successfully loaded {len(reviews)} reviews")

                return driver.page_source

            except TimeoutException:
                logger.warning(f"Timeout while loading content (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            except WebDriverException as e:
                logger.error(f"WebDriver error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)

        logger.error("Failed to load dynamic content after all retries")
        return None

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")

def main():
    args = parse_arguments()
    domain = args.domain
    page = 1
    start_page = 1
    reviews = []

    # Only initialize these if needed
    reviews_by_location = {} if args.visualize else None
    keyword_analysis = {} if args.analyze else None

    # Check if allowed by robots.txt
    ua = UserAgent()
    user_agent = ua.random
    if not is_allowed_by_robots_txt(
            f"https://www.trustpilot.com/review/{domain}", user_agent
    ):
        logger.error("Scraping is disallowed by robots.txt.")
        return

    while True:
        try:
            url = generate_url(domain, page, args)
            html = get_html_with_retry(url, args.retry)
            if html is None:
                logger.info(f"Page {page} does not exist. Stopping.")
                break
            page_reviews = get_reviews_data(html)
            logger.info(f"Found {len(page_reviews)} reviews on page {page}")
            if not page_reviews:
                break
            page_reviews = process_reviews(page_reviews)
            reviews.extend(page_reviews)
            if page % 10 == 0:
                save_reviews(reviews, domain, start_page, page)
                reviews = []
                start_page = page + 1
            page += 1
            time.sleep(random.randint(5, 10) / 10)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Error fetching page {page}: {e}")
            break