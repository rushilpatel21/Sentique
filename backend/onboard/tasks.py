from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from app_store_scraper import AppStore
from google_play_scraper import Sort
from google_play_scraper.constants.element import ElementSpecs
from google_play_scraper.constants.regex import Regex
from google_play_scraper.constants.request import Formats
from google_play_scraper.utils.request import post
from typing import List, Tuple
import praw
import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
from time import sleep
import logging
from .models import UserData
from reviews.models import Review
from django.db import transaction, IntegrityError
from .models import CustomUser as UserProfile
from bs4 import BeautifulSoup
import csv
import os
import tempfile
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_user_data(self, user_id):
    try:
        print(user_id)
        user_data = UserData.objects.get(user_id=user_id)
        print(user_data)
        logger.info(f"Starting data processing for user {user_id}")

        steps = {
            1: lambda: step_1(user_data, user_id),
            2: lambda: step_2(user_data,user_id)
        }

        if user_data.step_status["step1"] == "pending":
            user_data.step_status["step1_substeps"] = {
                "substep1": "pending",  # App Store
                "substep2": "pending",  # Google Play
                "substep3": "pending",  # Reddit
                "substep4": "pending",  # Trustpilot
                "substep5": "pending",  # Twitter
            }
            user_data.save()
            logger.info("Initialized sub-steps for Step 1")

        for step_num in range(user_data.current_step, 3):
            try:
                print(step_num)
                steps[step_num]()
                user_data.step_status[f"step{step_num}"] = "completed"
                user_data.current_step = step_num + 1
                user_data.save()
                logger.info(f"Completed Step {step_num}")
            except Exception as e:
                user_data.step_status[f"step{step_num}"] = "failed"
                user_data.save()
                logger.error(f"Failed Step {step_num}: {str(e)}")
                raise self.retry(exc=e, countdown=300)

        user_data.overall_status = "completed"
        user_data.save()
        logger.info(f"Data processing completed for user {user_id}")

    except MaxRetriesExceededError:
        user_data.overall_status = "failed"
        user_data.save()
        logger.error(f"Max retries exceeded for user {user_id}")

# Step 1: Scraping with 5 sub-steps
def step_1(user_data, user_id):
    substeps = {
        1: lambda: scrape_source_1(user_data, user_id),  # App Store
        2: lambda: scrape_source_2(user_data,user_id),  # Google Play
        3: lambda: scrape_source_3(user_data,user_id),  # Reddit
        4: lambda: scrape_source_4(user_data,user_id),  # Trustpilot
        5: lambda: scrape_source_5(user_data,user_id),  # Twitter
    }

    for substep_num in range(1, 6):
        if user_data.step_status["step1_substeps"][f"substep{substep_num}"] == "pending":
            try:
                substeps[substep_num]()
                user_data.step_status["step1_substeps"][f"substep{substep_num}"] = "completed"
                user_data.save()
                logger.info(f"Completed Sub-step {substep_num} of Step 1")
            except Exception as e:
                user_data.step_status["step1_substeps"][f"substep{substep_num}"] = "failed"
                user_data.save()
                logger.error(f"Failed Sub-step {substep_num} of Step 1: {str(e)}")
                raise e

# Sub-step 1: App Store Scraper
def scrape_source_1(user_data,user_id, country="us", total_reviews=2000, batch_size=1000):
    try:
        profile = UserProfile.objects.get(id=user_id)
        app_id = profile.apple_app_store_id
        app_name = profile.apple_app_store_name
        if not app_id or not app_name:
            raise ValueError("Apple App Store ID or name missing")
    except UserProfile.DoesNotExist:
        raise ValueError("User profile not found")

    logger.info(f"Starting App Store scraping for {app_name} (ID: {app_id})")
    app = AppStore(country=country, app_name=app_name, app_id=app_id)
    reviews_collected = user_data.reviews.filter(source="appstore").count()

    while reviews_collected < total_reviews:
        remaining = total_reviews - reviews_collected
        fetch_count = min(batch_size, remaining)

        try:
            app.review(how_many=fetch_count)
            for review in app.reviews:
                try:
                    Review.objects.create(
                        user_data=user_data,
                        review_id=str(review.get('reviewId', f"appstore_{reviews_collected}")),
                        date=review.get('date', datetime.now()),
                        rating=review.get('rating', 0),
                        source="appstore",
                        review=review.get('review', ''),
                        title=review.get('title', ''),
                        username=review.get('userName', ''),
                        url=f"https://apps.apple.com/{country}/app/{app_name}/id{app_id}",
                        comments=[],
                        language=country,
                    )
                except IntegrityError as e:
                    # Log the error or print it for debugging
                    print(f"Skipping review due to IntegrityError: {e}")
                    continue
                reviews_collected += 1

            logger.info(f"Collected {reviews_collected}/{total_reviews} App Store reviews")
            app.reviews = []
            sleep(1)  # Avoid rate limiting

        except Exception as e:
            logger.error(f"Error scraping App Store: {str(e)}")
            raise e

    logger.info(f"App Store scraping completed. Total reviews: {reviews_collected}")

# Sub-step 2: Google Play Scraper
MAX_COUNT_EACH_FETCH = 199

class _ContinuationToken:
    __slots__ = ("token", "lang", "country", "sort", "count", "filter_score_with", "filter_device_with")

    def __init__(self, token, lang, country, sort, count, filter_score_with, filter_device_with):
        self.token = token
        self.lang = lang
        self.country = country
        self.sort = sort
        self.count = count
        self.filter_score_with = filter_score_with
        self.filter_device_with = filter_device_with

def _fetch_review_items(url, app_id, sort, count, filter_score_with, filter_device_with, pagination_token):
    dom = post(
        url,
        Formats.Reviews.build_body(app_id, sort, count, "null" if filter_score_with is None else filter_score_with,
                                   "null" if filter_device_with is None else filter_device_with, pagination_token),
        {"content-type": "application/x-www-form-urlencoded"},
    )
    match = json.loads(Regex.REVIEWS.findall(dom)[0])
    return json.loads(match[0][2])[0], json.loads(match[0][2])[-2][-1]

def reviews(app_id, lang="en", country="us", sort=Sort.MOST_RELEVANT, count=100, filter_score_with=None,
            filter_device_with=None, continuation_token=None) -> Tuple[List[dict], _ContinuationToken]:
    sort = sort.value
    if continuation_token:
        token = continuation_token.token
        if token is None:
            return [], continuation_token
        lang = continuation_token.lang
        country = continuation_token.country
        sort = continuation_token.sort
        count = continuation_token.count
        filter_score_with = continuation_token.filter_score_with
        filter_device_with = continuation_token.filter_device_with
    else:
        token = None

    url = Formats.Reviews.build(lang=lang, country=country)
    _fetch_count = count
    result = []

    while _fetch_count > 0:
        fetch_count = min(_fetch_count, MAX_COUNT_EACH_FETCH)
        try:
            review_items, token = _fetch_review_items(url, app_id, sort, fetch_count, filter_score_with, filter_device_with, token)
            for review in review_items:
                result.append({k: spec.extract_content(review) for k, spec in ElementSpecs.Review.items()})
            _fetch_count = count - len(result)
            if isinstance(token, list):
                token = None
                break
        except (TypeError, IndexError):
            token = continuation_token.token if continuation_token else None
            break

    return result, _ContinuationToken(token, lang, country, sort, count, filter_score_with, filter_device_with)

def scrape_source_2(user_data, user_id,country="us", total_reviews=2000, batch_size=1000):
    try:
        profile = UserProfile.objects.get(id=user_id)
        app_id = profile.google_play_app_id
        if not app_id:
            raise ValueError("Google Play App ID missing")
    except UserProfile.DoesNotExist:
        raise ValueError("User profile not found")

    logger.info(f"Starting Google Play scraping for {app_id}")
    reviews_collected = user_data.reviews.filter(source="googleplay").count()
    continuation_token = None

    while reviews_collected < total_reviews:
        remaining = total_reviews - reviews_collected
        fetch_count = min(batch_size, remaining)

        try:
            new_result, continuation_token = reviews(
                app_id=app_id,
                count=fetch_count,
                lang="en",
                country=country,
                sort=Sort.MOST_RELEVANT,
                filter_score_with=None,
                continuation_token=continuation_token
            )
            if not new_result:
                break

            for review in new_result:
                try:
                    Review.objects.create(
                        user_data=user_data,
                        review_id=review.get('reviewId', f"googleplay_{reviews_collected}"),
                        date=review.get('at', datetime.now().isoformat()),
                        rating=review.get('score', 0),
                        source="googleplay",
                        review=review.get('content', ''),
                        title=None,
                        username=review.get('userName', ''),
                        url=f"https://play.google.com/store/apps/details?id={app_id}",
                        comments=[],
                        language=country,
                    )
                except IntegrityError as e:
                    # Log the error or print it for debugging
                    print(f"Skipping review due to IntegrityError: {e}")
                    continue
                reviews_collected += 1

            logger.info(f"Collected {reviews_collected}/{total_reviews} Google Play reviews")
            sleep(1)  # Avoid rate limiting

        except Exception as e:
            logger.error(f"Error scraping Google Play: {str(e)}")
            raise e

    logger.info(f"Google Play scraping completed. Total reviews: {reviews_collected}")

# Sub-step 3: Reddit Scraper
def scrape_source_3(user_data, user_id, subreddit="uber", total_reviews=2000, batch_size=1000):
    logger.info(f"Starting Reddit scraping for subreddit '{subreddit}'")
    reddit = praw.Reddit(
        client_id="qApJC9H-Od2AJU0eQJN84g",
        client_secret="19zsvlAHsCJMNithtcHUg0jI9Y4f3A",
        user_agent="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 9_4_2) AppleWebKit/601.24 (KHTML, like Gecko) Chrome/50.0.1832.351 Safari/603"
    )
    reviews_collected = user_data.reviews.filter(source="reddit").count()
    posts_list = []

    for submission in reddit.subreddit(subreddit).new(limit=None):
        if reviews_collected >= total_reviews:
            break

        try:
            post_data = {
                "review_id": submission.id,
                "date": datetime.fromtimestamp(submission.created_utc),
                "rating": float(submission.score),
                "source": "reddit",
                "review": submission.selftext,
                "title": submission.title,
                "username": str(submission.author) if submission.author else None,
                "url": submission.url,
                "language": "en",
            }
            posts_list.append(post_data)
            reviews_collected += 1

            if len(posts_list) >= batch_size:
                for post in posts_list:
                    Review.objects.create(user_data=user_data, **post)
                logger.info(f"Collected {reviews_collected}/{total_reviews} Reddit posts")
                posts_list = []

        except Exception as e:
            logger.error(f"Error scraping Reddit: {str(e)}")
            raise e

    if posts_list:
        for post in posts_list:
            Review.objects.create(user_data=user_data, **post)
    logger.info(f"Reddit scraping completed. Total posts: {reviews_collected}")

# Sub-step 4: Trustpilot Scraper
session = requests.Session()

def get_html(url: str) -> str:
    ua = UserAgent()
    session.headers.update({"User-Agent": ua.random})
    response = session.get(url, timeout=10)
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        return None
    response.raise_for_status()

def get_reviews_data(html: str) -> list[dict]:

    soup = BeautifulSoup(html, "lxml")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    return json.loads(script_tag.string)["props"]["pageProps"]["reviews"]

def iso_to_datetime(iso_str: str) -> datetime:
    if iso_str:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return datetime.now()

def parse_review(review: dict) -> dict:
    dates = review.get("dates", {})
    consumer = review.get("consumer", {})
    return {
        "review_id": review.get("id"),
        "date": iso_to_datetime(dates.get("publishedDate")),
        "rating": review.get("rating", 0),
        "source": "trustpilot",
        "review": review.get("text", ""),
        "title": review.get("title", ""),
        "username": consumer.get("displayName", ""),
        "url": f"https://www.trustpilot.com/reviews/{review.get('id')}",
        "comments": [],
        "language": review.get("language", "en"),
    }

def scrape_source_4(user_data, user_id, total_reviews=2000, batch_size=1000):
    try:
        profile = UserProfile.objects.get(id=user_id)
        domain = profile.website_url
    except UserProfile.DoesNotExist:
        raise ValueError("User profile not found")

    logger.info(f"Starting Trustpilot scraping for domain {domain}")
    reviews_collected = user_data.reviews.filter(source="trustpilot").count()
    page = 1
    reviews_batch = []

    while reviews_collected < total_reviews:
        url = f"https://www.trustpilot.com/review/{domain}?page={page}"
        try:
            html = get_html(url)
            if not html:
                logger.info(f"No more pages available at page {page}")
                break

            page_reviews = get_reviews_data(html)
            if not page_reviews:
                logger.info(f"No reviews found on page {page}")
                break

            for review in page_reviews:
                if reviews_collected >= total_reviews:
                    break
                parsed_review = parse_review(review)
                reviews_batch.append(parsed_review)
                reviews_collected += 1

                if len(reviews_batch) >= batch_size:
                    for review_data in reviews_batch:
                        try:
                            Review.objects.create(user_data=user_data, **review_data)
                        except IntegrityError as e:
                            # Log the error or print it for debugging
                            print(f"Skipping review due to IntegrityError: {e}")
                            continue
                    logger.info(f"Collected {reviews_collected}/{total_reviews} Trustpilot reviews")
                    reviews_batch = []

            page += 1
            sleep(1)  # Avoid rate limiting

        except Exception as e:
            logger.error(f"Error scraping Trustpilot page {page}: {str(e)}")
            raise e

    if reviews_batch:
        for review_data in reviews_batch:
            Review.objects.create(user_data=user_data, **review_data)
    logger.info(f"Trustpilot scraping completed. Total reviews: {reviews_collected}")

# Sub-step 5: Twitter Scraper
def scrape_source_5(user_data,user_id, total_reviews=1000, batch_size=1000):
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    api_key = "9bc607ac228c4f43b27aec7203fe7bba"
    headers = {"X-API-Key": api_key}
    query = "+uber -eats -ubereats -stock -$UBER - lang:en -is:retweet until:2025-01-21 min_faves:10"
    query_type = "Top"

    logger.info("Starting Twitter scraping")
    reviews_collected = user_data.reviews.filter(source="twitter").count()
    cursor = " "
    tweets_batch = []
    max_iterations = 1000

    for iteration in range(max_iterations):
        if reviews_collected >= total_reviews:
            break

        querystring = {"queryType": query_type, "query": query, "cursor": cursor}
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            if response.status_code != 200:
                logger.error(f"Twitter API error: {response.status_code} - {response.text}")
                break

            data = response.json()
            tweets = data.get("tweets", [])
            if not tweets:
                logger.info("No more tweets found")
                break

            for tweet in tweets:
                if reviews_collected >= total_reviews:
                    break
                tweet_data = {
                    "review_id": tweet["id"],
                    "date": datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S %z %Y"),
                    "rating": float(tweet.get("favoriteCount", 0)),
                    "source": "twitter",
                    "review": tweet["text"],
                    "title": "None",
                    "username": tweet["author"]["userName"],
                    "url": tweet["url"],
                    "comments": [],
                    "language": tweet["lang"],
                }
                tweets_batch.append(tweet_data)
                reviews_collected += 1

                if len(tweets_batch) >= batch_size:
                    for tweet in tweets_batch:
                        try:
                            Review.objects.create(user_data=user_data, **tweet)
                        except IntegrityError as e:
                            # Log the error or print it for debugging
                            print(f"Skipping review due to IntegrityError: {e}")
                            continue
                    logger.info(f"Collected {reviews_collected}/{total_reviews} Twitter tweets")
                    tweets_batch = []

            cursor = data.get("next_cursor")
            if not cursor or cursor == " ":
                logger.info("No new cursor found")
                break

            sleep(1)  # Avoid rate limiting

        except Exception as e:
            logger.error(f"Error scraping Twitter: {str(e)}")
            raise e

    if tweets_batch:
        for tweet in tweets_batch:
            Review.objects.create(user_data=user_data, **tweet)
    logger.info(f"Twitter scraping completed. Total tweets: {reviews_collected}")


def step_2(user_data, user_id):
    logger.info(f"Step 2 Started for all reviews")
    api_url = "https://3efb-34-32-158-123.ngrok-free.app/analyze_csv"

    # Get total count first
    total_unprocessed = Review.objects.filter(sentiment__isnull=True).count()
    logger.info(f"Found {total_unprocessed} reviews with empty sentiment")

    if total_unprocessed == 0:
        logger.warning("No reviews with empty sentiment found.")
        return

    BATCH_SIZE = 1500
    total_processed = 0

    # Continue processing until all records are processed
    while True:
        # Get next batch, excluding already processed IDs
        batch_reviews = Review.objects.filter(
            sentiment__isnull=True
        ).order_by('id')[:BATCH_SIZE]

        if not batch_reviews.exists():
            logger.info("No more unprocessed reviews found.")
            break

        batch_size = batch_reviews.count()
        logger.info(f"Processing batch of {batch_size} reviews")

        # Create CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as temp_file:
            temp_filename = temp_file.name
            logger.debug(f"Created temporary file: {temp_filename}")
            csv_writer = csv.writer(temp_file)
            csv_writer.writerow(['id', 'review_id', 'text'])

            for review in batch_reviews:
                csv_writer.writerow([str(review.id), review.review_id, review.review])

        try:
            # Send to API
            with open(temp_filename, 'rb') as file:
                files = {'file': (os.path.basename(temp_filename), file, 'text/csv')}
                response = requests.post(api_url, files=files)
                response.raise_for_status()

            # Process response
            if 'text/csv' in response.headers.get('content-type', '').lower():
                results_filename = tempfile.mktemp(suffix='.csv')
                with open(results_filename, 'wb') as f:
                    f.write(response.content)

                # Track which reviews were actually updated
                with open(results_filename, 'r', newline='') as f:
                    csv_reader = csv.DictReader(f)

                    with transaction.atomic():
                        for row in csv_reader:
                            review_id = row.get('review_id')
                            if not review_id:
                                logger.warning(f"Missing review_id in API response row")
                                continue

                            try:
                                # Use get() to find exactly one record
                                review = Review.objects.get(review_id=review_id)

                                # Only update if sentiment is still null
                                if review.sentiment is None:
                                    review.sentiment = row.get('sentiment')
                                    review.category = row.get('category')
                                    review.save()
                                    total_processed += 1
                                else:
                                    logger.debug(f"Review {review_id} already has sentiment: {review.sentiment}")
                            except Review.DoesNotExist:
                                logger.error(f"Review with review_id {review_id} not found")
                            except Review.MultipleObjectsReturned:
                                # Handle duplicate review_ids
                                logger.error(f"Multiple reviews found with review_id {review_id}")
                                reviews = Review.objects.filter(review_id=review_id)
                                for rev in reviews:
                                    if rev.sentiment is None:
                                        rev.sentiment = row.get('sentiment')
                                        rev.category = row.get('category')
                                        rev.save()
                                        total_processed += 1

                # Check for records that weren't updated
                # Clean up
                os.remove(results_filename)
            else:
                logger.warning(f"Unexpected content type: {response.headers.get('content-type')}")

        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}", exc_error=True)
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        # Check if we've processed all records
        remaining = Review.objects.filter(sentiment__isnull=True).count()
        logger.info(f"Processed {total_processed} reviews so far. {remaining} reviews still need processing.")

        if remaining == 0 or len(batch_reviews) < BATCH_SIZE:
            break

    logger.info(
        f"Step 2 Completed. Total processed: {total_processed}, Remaining: {Review.objects.filter(sentiment__isnull=True).count()}")

