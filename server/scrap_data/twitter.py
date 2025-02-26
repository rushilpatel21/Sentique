import time
import random
import pandas as pd
import json
import re
import os
import logging
from datetime import datetime, timedelta
from urllib.parse import quote
from playwright.sync_api import sync_playwright, TimeoutError, Error
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    def __init__(
        self, 
        headless=False,
        user_data_dir=None,
        slow_mo=50,
        timeout=30000,
        proxy=None
    ):
        """
        Initialize the Twitter scraper
        
        Args:
            headless (bool): Run browser in headless mode
            user_data_dir (str): Path to browser user data directory for logged-in session
            slow_mo (int): Slow down operations by specified milliseconds (helps avoid detection)
            timeout (int): Default timeout for operations in milliseconds
            proxy (dict): Proxy configuration (e.g., {'server': 'http://proxy.example.com:8080'})
        """
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def start_browser(self):
        """Initialize the browser and create a new page"""
        self.playwright = sync_playwright().start()
        
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            "--disable-web-security",
        ]
        
        browser_options = {
            "headless": self.headless,
            "args": browser_args,
            "slow_mo": self.slow_mo
        }
        
        if self.proxy:
            browser_options["proxy"] = self.proxy
            
        # Use persistent context if user_data_dir provided
        if self.user_data_dir:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                **browser_options
            )
            self.browser = None  # Not needed with persistent context
        else:
            self.browser = self.playwright.chromium.launch(**browser_options)
            self.context = self.browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
        
        # Add cookies/localStorage if needed for authentication
        
        self.page = self.context.new_page()
        
        # Set up request interception if needed
        # self.page.route("**/*", self._handle_route)
        
        # Set extra headers to appear more like a real browser
        self.page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://x.com/",
            "DNT": "1"  # Do Not Track
        })
        
        return self.playwright

    def close(self):
        """Close the browser and all resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _random_delay(self, min_seconds=1.0, max_seconds=3.0):
        """Add a random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay

    def _scroll_page(self, pixel_distance=None):
        """Scroll the page down with a random amount if not specified"""
        if pixel_distance is None:
            # Scroll between 40% to 80% of viewport height
            pixel_distance = self.page.evaluate(
                "Math.floor(Math.random() * (window.innerHeight * 0.8 - window.innerHeight * 0.4) + window.innerHeight * 0.4)"
            )
        
        self.page.evaluate(f"window.scrollBy(0, {pixel_distance})")
        return pixel_distance

    def check_login_status(self):
        """Check if the current session is logged in to Twitter/X"""
        try:
            # Navigate to profile menu to check if logged in
            self.page.goto("https://x.com/home", timeout=self.timeout)
            
            # Wait for either the login button (not logged in) or the tweet button (logged in)
            logged_in = False
            try:
                # Check for tweet button or profile menu
                logged_in = self.page.wait_for_selector(
                    'a[href="/compose/tweet"] div[role="button"], div[data-testid="primaryColumn"]',
                    timeout=10000
                ) is not None
            except:
                logged_in = False
                
            return logged_in
            
        except Exception as e:
            logger.error(f"Error checking login status: {str(e)}")
            return False

    def login(self, username, password):
        """Login to Twitter/X with the provided credentials"""
        try:
            # Navigate to login page
            self.page.goto("https://twitter.com/i/flow/login", timeout=self.timeout)
            
            # Wait for the username field
            self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            
            # Enter username
            self.page.fill('input[autocomplete="username"]', username)
            self._random_delay(0.5, 1.5)
            
            # Click the Next button
            self.page.click('div[role="button"]:has-text("Next")')
            
            # Wait for password field
            self.page.wait_for_selector('input[type="password"]', timeout=10000)
            
            # Enter password
            self.page.fill('input[type="password"]', password)
            self._random_delay(0.5, 1.5)
            
            # Click the Login button
            self.page.click('div[role="button"]:has-text("Log in")')
            
            # Wait for home timeline to confirm successful login
            self.page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=20000)
            
            logger.info("Successfully logged in to Twitter/X")
            return True
            
        except Exception as e:
            logger.error(f"Failed to login: {str(e)}")
            return False

    def build_search_query(
        self, 
        search_terms, 
        language=None, 
        exclude_links=False, 
        min_replies=None, 
        min_likes=None, 
        min_retweets=None,
        from_date=None,
        to_date=None,
        from_accounts=None,
        exclude_accounts=None,
        include_hashtags=True
    ):
        """
        Build an advanced search query string for Twitter/X
        
        Args:
            search_terms: String or list of search terms
            language: Language code (e.g. "en" for English)
            exclude_links: Exclude tweets with links
            min_replies: Minimum number of replies
            min_likes: Minimum number of likes
            min_retweets: Minimum number of retweets
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            from_accounts: List of accounts to include
            exclude_accounts: List of accounts to exclude
            include_hashtags: Include hashtag versions of search terms
            
        Returns:
            URL-encoded search query string
        """
        # Convert single term to list
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        
        # Basic query with all terms (using OR)
        query_parts = [f'({" OR ".join(search_terms)})']
        
        # Add hashtag versions
        if include_hashtags:
            hashtags = [f'#{term.replace(" ", "")}' for term in search_terms]
            query_parts.append(f'({" OR ".join(hashtags)})')
        
        # Language filter
        if language:
            query_parts.append(f'lang:{language}')
        
        # Exclude links
        if exclude_links:
            query_parts.append('-filter:links')
        
        # Min interactions
        if min_replies:
            query_parts.append(f'min_replies:{min_replies}')
        if min_likes:
            query_parts.append(f'min_faves:{min_likes}')
        if min_retweets:
            query_parts.append(f'min_retweets:{min_retweets}')
        
        # Date range
        if from_date:
            query_parts.append(f'since:{from_date}')
        if to_date:
            query_parts.append(f'until:{to_date}')
        
        # Account filters
        if from_accounts:
            if isinstance(from_accounts, str):
                from_accounts = [from_accounts]
            account_query = " OR ".join([f'from:{account.replace("@", "")}' for account in from_accounts])
            query_parts.append(f'({account_query})')
        
        if exclude_accounts:
            if isinstance(exclude_accounts, str):
                exclude_accounts = [exclude_accounts]
            for account in exclude_accounts:
                query_parts.append(f'-from:{account.replace("@", "")}')
        
        # Join all parts with spaces
        query = " ".join(query_parts)
        
        # URL encode the query
        encoded_query = quote(query)
        return encoded_query

    def extract_tweet_data(self, article_element):
        """
        Extract structured data from a tweet article element
        
        Args:
            article_element: BeautifulSoup article object representing a tweet
            
        Returns:
            Dictionary with tweet data or None if extraction failed
        """
        try:
            # Get tweet ID from article data-testid (fallback to a random ID)
            tweet_id = article_element.get("data-testid", f"tweet-{random.randint(10000, 99999)}")
            
            # EXTRACT USER INFO
            user_info = {}
            user_elem = article_element.select_one('div[data-testid="User-Name"]')
            if user_elem:
                # Username (handle)
                username_link = user_elem.select_one('a[role="link"] div[dir="ltr"]')
                if username_link:
                    username = username_link.text.strip()
                    if username.startswith('@'):
                        user_info['username'] = username[1:]  # Remove @ symbol
                    else:
                        user_info['username'] = username
                
                # Display name
                display_name_elem = user_elem.select_one('a[role="link"] div span')
                if display_name_elem:
                    user_info['display_name'] = display_name_elem.text.strip()
                
                # Profile link
                profile_link = user_elem.select_one('a[role="link"]')
                if profile_link and 'href' in profile_link.attrs:
                    user_info['profile_url'] = f"https://twitter.com{profile_link['href']}"
            
            # EXTRACT TWEET CONTENT
            tweet_content = {}
            
            # Main text content
            text_div = article_element.select_one('div[data-testid="tweetText"]')
            if text_div:
                # Get plain text but preserve paragraph breaks
                paragraphs = []
                for elem in text_div.find_all(['span', 'br']):
                    if elem.name == 'br':
                        paragraphs.append('\n')
                    elif elem.text.strip():
                        paragraphs.append(elem.text)
                
                tweet_content['text'] = ''.join(paragraphs).strip()
                
                # Extract hashtags
                hashtags = []
                for hashtag_elem in text_div.select('a[href^="/hashtag/"]'):
                    hashtags.append(hashtag_elem.text.strip())
                
                if hashtags:
                    tweet_content['hashtags'] = hashtags
                
                # Extract mentions
                mentions = []
                for mention_elem in text_div.select('a[href^="/"]'):
                    href = mention_elem.get('href', '')
                    if href.startswith('/') and not href.startswith(('/search', '/hashtag')):
                        mentions.append(mention_elem.text.strip())
                
                if mentions:
                    tweet_content['mentions'] = mentions
            
            # Media content
            media_container = article_element.select_one('div[data-testid="tweetPhoto"], div[data-testid="videoPlayer"]')
            if media_container:
                if media_container.get('data-testid') == 'videoPlayer':
                    tweet_content['has_video'] = True
                else:
                    tweet_content['has_image'] = True
                    
                    # Try to extract image URLs
                    image_urls = []
                    for img in media_container.select('img[src]'):
                        if 'src' in img.attrs and not img['src'].endswith('svg'):
                            image_urls.append(img['src'])
                    
                    if image_urls:
                        tweet_content['image_urls'] = image_urls
            
            # EXTRACT METADATA
            metadata = {}
            
            # Timestamp
            time_elem = article_element.select_one('time')
            if time_elem and 'datetime' in time_elem.attrs:
                metadata['timestamp'] = time_elem['datetime']
                
                # Also get the human-readable time
                if time_elem.has_attr('title'):
                    metadata['time_display'] = time_elem['title']
            
            # Tweet URL
            tweet_link = article_element.select_one('a[href*="/status/"]')
            if tweet_link and 'href' in tweet_link.attrs:
                metadata['tweet_url'] = f"https://twitter.com{tweet_link['href']}"
                # Extract tweet ID from URL
                status_match = re.search(r'/status/(\d+)', tweet_link['href'])
                if status_match:
                    metadata['tweet_id'] = status_match.group(1)
            
            # EXTRACT ENGAGEMENT METRICS
            engagement = {}
            
            # Reply count
            reply_elem = article_element.select_one('div[data-testid="reply"]')
            if reply_elem:
                count_span = reply_elem.select_one('span[data-testid="app-text-transition-container"]')
                if count_span:
                    reply_count = count_span.text.strip()
                    engagement['replies'] = self._parse_count(reply_count)
            
            # Retweet count
            retweet_elem = article_element.select_one('div[data-testid="retweet"]')
            if retweet_elem:
                count_span = retweet_elem.select_one('span[data-testid="app-text-transition-container"]')
                if count_span:
                    retweet_count = count_span.text.strip()
                    engagement['retweets'] = self._parse_count(retweet_count)
            
            # Like count
            like_elem = article_element.select_one('div[data-testid="like"]')
            if like_elem:
                count_span = like_elem.select_one('span[data-testid="app-text-transition-container"]')
                if count_span:
                    like_count = count_span.text.strip()
                    engagement['likes'] = self._parse_count(like_count)
            
            # View count (if available)
            view_elem = article_element.select_one('div[data-testid="analyticsButton"], a[href*="/analytics"]')
            if view_elem:
                count_span = view_elem.select_one('span[data-testid="app-text-transition-container"]')
                if count_span:
                    view_count = count_span.text.strip()
                    engagement['views'] = self._parse_count(view_count)
            
            # Check if tweet is a retweet or quote
            is_retweet = False
            retweet_indicator = article_element.select_one('span:contains("Retweeted")')
            if retweet_indicator:
                is_retweet = True
            
            # Construct the full tweet data object
            tweet_data = {
                'user': user_info,
                'content': tweet_content,
                'metadata': metadata,
                'engagement': engagement,
                'is_retweet': is_retweet,
                'extracted_at': datetime.now().isoformat()
            }
            
            return tweet_data
            
        except Exception as e:
            logger.error(f"Error extracting tweet data: {str(e)}")
            return None

    def _parse_count(self, count_str):
        """Convert string count ('12K', '1.5M', etc.) to integer"""
        if not count_str or count_str == '':
            return 0
            
        try:
            # Remove commas
            count_str = count_str.replace(',', '')
            
            # Handle K, M abbreviations
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(count_str)
                
        except ValueError:
            return 0

    def extract_tweets_from_page(self):
        """
        Extract all tweets from the currently loaded page
        
        Returns:
            List of tweet data dictionaries
        """
        # Get the page content and parse with BeautifulSoup
        html = self.page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all tweet articles
        articles = soup.find_all("article", {"data-testid": lambda x: x and x.startswith("tweet")})
        
        tweets_data = []
        for article in articles:
            tweet_data = self.extract_tweet_data(article)
            if tweet_data:
                # Check if we've already seen this tweet (avoid duplicates)
                is_duplicate = False
                for existing in tweets_data:
                    if (tweet_data.get('metadata', {}).get('tweet_id') == 
                        existing.get('metadata', {}).get('tweet_id')):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    tweets_data.append(tweet_data)
        
        return tweets_data

    def scrape_search_results(
        self,
        search_terms,
        output_file=None,
        max_tweets=500,
        min_tweets=100,
        max_scrolls=50,
        language="en",
        exclude_links=False,
        min_replies=None,
        min_likes=None,
        min_retweets=None,
        from_date=None,
        to_date=None,
        from_accounts=None,
        exclude_accounts=None,
        include_hashtags=True,
        search_type="latest"  # Can be "latest", "top", "photos", "videos"
    ):
        """
        Scrape tweets from search results
        
        Args:
            search_terms: String or list of search terms
            output_file: Path to save results (CSV/JSON)
            max_tweets: Maximum tweets to collect
            min_tweets: Minimum tweets to collect before stopping
            max_scrolls: Maximum number of page scrolls
            language: Language filter (e.g., "en" for English)
            And other search parameters...
            
        Returns:
            List of tweet data dictionaries
        """
        # Build the search query
        encoded_query = self.build_search_query(
            search_terms=search_terms,
            language=language,
            exclude_links=exclude_links,
            min_replies=min_replies,
            min_likes=min_likes,
            min_retweets=min_retweets,
            from_date=from_date,
            to_date=to_date,
            from_accounts=from_accounts,
            exclude_accounts=exclude_accounts,
            include_hashtags=include_hashtags
        )
        
        # Determine search type parameter
        search_tab = "f=live"  # default to latest
        if search_type == "top":
            search_tab = "f=top"
        elif search_type == "photos":
            search_tab = "f=image"
        elif search_type == "videos":
            search_tab = "f=video"
        
        # Search URL
        search_url = f"https://twitter.com/search?q={encoded_query}&{search_tab}"
        logger.info(f"Navigating to search URL: {search_url}")
        
        tweets_data = []
        seen_tweet_ids = set()
        consecutive_no_new_tweets = 0
        
        try:
            # Navigate to search URL
            self.page.goto(search_url, timeout=self.timeout)
            
            # Wait for content to load
            self.page.wait_for_selector('article[data-testid^="tweet"]', timeout=20000)
            logger.info("Initial tweets loaded")
            
            # Initial extraction
            initial_tweets = self.extract_tweets_from_page()
            logger.info(f"Initial extraction: found {len(initial_tweets)} tweets")
            
            for tweet in initial_tweets:
                tweet_id = tweet.get('metadata', {}).get('tweet_id')
                if tweet_id and tweet_id not in seen_tweet_ids:
                    tweets_data.append(tweet)
                    seen_tweet_ids.add(tweet_id)
            
            # Scroll to load more tweets
            for i in range(max_scrolls):
                # Check if we have enough tweets
                if len(tweets_data) >= max_tweets:
                    logger.info(f"Reached target of {max_tweets} tweets. Stopping.")
                    break
                
                # Random delay to appear more human-like
                self._random_delay(1.5, 4.0)
                
                # Scroll down
                scroll_amount = self._scroll_page()
                logger.info(f"Scrolled down {scroll_amount} pixels")
                
                # Wait for new content to load
                try:
                    # Look for a loading indicator or wait for network idle
                    self.page.wait_for_load_state("networkidle", timeout=5000)
                    
                    # Sometimes need to wait for specific elements to appear
                    self.page.wait_for_function(
                        "document.querySelectorAll('article[data-testid^=\"tweet\"]').length > 0",
                        timeout=5000
                    )
                except TimeoutError:
                    logger.warning(f"Timeout waiting for new tweets on scroll {i+1}")
                
                # Extract tweets from the current page state
                new_tweets = self.extract_tweets_from_page()
                
                # Filter out tweets we've already seen
                truly_new_tweets = []
                for tweet in new_tweets:
                    tweet_id = tweet.get('metadata', {}).get('tweet_id')
                    if tweet_id and tweet_id not in seen_tweet_ids:
                        truly_new_tweets.append(tweet)
                        seen_tweet_ids.add(tweet_id)
                
                # Add new tweets to our collection
                tweets_data.extend(truly_new_tweets)
                
                # Log progress
                logger.info(f"Scroll {i+1}/{max_scrolls}: Found {len(truly_new_tweets)} new tweets. Total: {len(tweets_data)}")
                
                # Check if we're still finding new tweets
                if not truly_new_tweets:
                    consecutive_no_new_tweets += 1
                    if consecutive_no_new_tweets >= 3:
                        logger.info("No new tweets in 3 consecutive scrolls. Stopping.")
                        break
                else:
                    consecutive_no_new_tweets = 0
                
                # Check if we have enough tweets and have reached minimum requirement
                if len(tweets_data) >= min_tweets and i >= 10:
                    logger.info(f"Collected {len(tweets_data)} tweets which meets minimum requirement. Stopping.")
                    break
                    
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
        
        # Save the results if an output file is specified
        if output_file and tweets_data:
            self.save_results(tweets_data, output_file)
        
        return tweets_data

    def save_results(self, tweets_data, output_file):
        """Save tweet data to CSV or JSON file"""
        if not tweets_data:
            logger.warning("No data to save")
            return
            
        try:
            # Determine file format based on extension
            file_ext = os.path.splitext(output_file)[1].lower()
            
            if file_ext == '.json':
                # Save as JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(tweets_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(tweets_data)} tweets to {output_file} (JSON)")
                
            elif file_ext == '.csv':
                # Flatten the nested structure for CSV
                flattened_data = []
                for tweet in tweets_data:
                    flat_tweet = {}
                    
                    # User info
                    for k, v in tweet.get('user', {}).items():
                        flat_tweet[f'user_{k}'] = v
                        
                    # Content
                    flat_tweet['text'] = tweet.get('content', {}).get('text', '')
                    flat_tweet['hashtags'] = ','.join(tweet.get('content', {}).get('hashtags', []))
                    flat_tweet['mentions'] = ','.join(tweet.get('content', {}).get('mentions', []))
                    flat_tweet['has_image'] = tweet.get('content', {}).get('has_image', False)
                    flat_tweet['has_video'] = tweet.get('content', {}).get('has_video', False)
                    
                    # Metadata
                    for k, v in tweet.get('metadata', {}).items():
                        flat_tweet[k] = v
                        
                    # Engagement
                    for k, v in tweet.get('engagement', {}).items():
                        flat_tweet[k] = v
                        
                    # Other fields
                    flat_tweet['is_retweet'] = tweet.get('is_retweet', False)
                    flat_tweet['extracted_at'] = tweet.get('extracted_at', '')
                    
                    flattened_data.append(flat_tweet)
                
                # Convert to DataFrame and save as CSV
                df = pd.DataFrame(flattened_data)
                df.to_csv(output_file, index=False, encoding='utf-8')
                logger.info(f"Saved {len(tweets_data)} tweets to {output_file} (CSV)")
                
            else:
                # Default to JSON if extension not recognized
                json_file = f"{os.path.splitext(output_file)[0]}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(tweets_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(tweets_data)} tweets to {json_file} (JSON)")
                
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

def main():
    # Create output directory if it doesn't exist
    os.makedirs("twitter_data", exist_ok=True)
    
    # Generate output filenames with timestamps
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_output = f"twitter_data/uber_tweets_{timestamp}.csv"
    json_output = f"twitter_data/uber_tweets_{timestamp}.json"
    
    # Get current date and date 6 months ago for default date range
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    today_str = today.strftime("%Y-%m-%d")
    six_months_ago_str = six_months_ago.strftime("%Y-%m-%d")
    
    # Initialize the scraper
    scraper = TwitterScraper(
        headless=False,  # Set to True for production use
        user_data_dir="C:/Users/Lenovo/AppData/Local/Chromium/User Data",  # Specify path to Chrome profile if needed
        slow_mo=50  # Slow down operations to avoid detection
    )
    
    try:
        # Start the browser
        scraper.start_browser()
        
        # Check if logged in and offer to login
        if not scraper.check_login_status():
            print("\nNot logged in to Twitter/X. Logging in would improve scraping results.")
            print("Do you want to log in? (y/n)")
            choice = input().lower()
            
            if choice == 'y':
                username = input("Enter your Twitter/X username or email: ")
                password = input("Enter your password: ")
                login_success = scraper.login(username, password)
                
                if not login_success:
                    print("Login failed. Continuing without login.")
        
        # Define search parameters for Uber
        print("\n--- Twitter Data Collection for Uber Research ---")
        print("Setting up search parameters...")
        
        # Define multiple search strategies to get comprehensive data
        search_strategies = [
            # Strategy 1: General Uber mentions
            {
                "search_terms": ["Uber", "UberEats", "Uber Technologies"],
                "min_tweets": 200,
                "max_tweets": 1000,
                "max_scrolls": 40,
                "language": "en",
                "search_type": "top",
                "output_file": f"twitter_data/uber_general_{timestamp}.csv"
            },
            
            # Strategy 2: Uber customer experiences
            {
                "search_terms": ["Uber experience", "Uber service", "Uber driver", "Uber customer"],
                "min_tweets": 100,
                "max_tweets": 500,
                "max_scrolls": 30,
                "language": "en",
                "search_type": "latest",
                "output_file": f"twitter_data/uber_experience_{timestamp}.csv"
            },
            
            # Strategy 3: Uber business and financial
            {
                                "search_terms": ["Uber business", "Uber stock", "Uber financial", "Uber revenue", "Uber profit"],
                "min_tweets": 100,
                "max_tweets": 400,
                "max_scrolls": 25,
                "language": "en",
                "search_type": "top",
                "min_likes": 5,  # Focus on more engaged content
                "from_date": six_months_ago_str,
                "to_date": today_str,
                "output_file": f"twitter_data/uber_business_{timestamp}.csv"
            },
            
            # Strategy 4: Uber controversy and news
            {
                "search_terms": ["Uber news", "Uber controversy", "Uber lawsuit", "Uber protest"],
                "min_tweets": 100,
                "max_tweets": 400,
                "max_scrolls": 25,
                "language": "en",
                "search_type": "latest",
                "output_file": f"twitter_data/uber_news_{timestamp}.csv"
            },
            
            # Strategy 5: From official Uber accounts
            {
                "search_terms": ["Uber"],
                "min_tweets": 50,
                "max_tweets": 300,
                "max_scrolls": 20,
                "language": "en",
                "from_accounts": ["Uber", "UberEats", "UberEng", "Uber_Support"],
                "output_file": f"twitter_data/uber_official_{timestamp}.csv"
            }
        ]
        
        # Run all search strategies
        all_tweets = []
        
        print(f"\nExecuting {len(search_strategies)} search strategies to gather comprehensive data...")
        
        for i, strategy in enumerate(search_strategies):
            print(f"\nStrategy {i+1}/{len(search_strategies)}: {' & '.join(strategy['search_terms'])}")
            
            # Extract strategy parameters
            search_terms = strategy["search_terms"]
            output_file = strategy["output_file"]
            strategy_params = {k: v for k, v in strategy.items() if k not in ["search_terms", "output_file"]}
            
            # Execute the search
            tweets = scraper.scrape_search_results(
                search_terms=search_terms,
                output_file=output_file,
                **strategy_params
            )
            
            print(f"Collected {len(tweets)} tweets for strategy {i+1}")
            all_tweets.extend(tweets)
        
        # Save combined results
        if all_tweets:
            # Remove duplicates by tweet ID
            seen_ids = set()
            unique_tweets = []
            
            for tweet in all_tweets:
                tweet_id = tweet.get('metadata', {}).get('tweet_id')
                if tweet_id and tweet_id not in seen_ids:
                    unique_tweets.append(tweet)
                    seen_ids.add(tweet_id)
            
            # Save to combined CSV and JSON files
            scraper.save_results(unique_tweets, csv_output)
            scraper.save_results(unique_tweets, json_output)
            
            print(f"\nSaved {len(unique_tweets)} unique tweets to combined outputs:")
            print(f"- CSV: {csv_output}")
            print(f"- JSON: {json_output}")
            
            # Print basic statistics
            user_count = len(set(t.get('user', {}).get('username') for t in unique_tweets if t.get('user', {}).get('username')))
            likes_count = sum(t.get('engagement', {}).get('likes', 0) for t in unique_tweets)
            retweets_count = sum(t.get('engagement', {}).get('retweets', 0) for t in unique_tweets)
            
            print("\nData Statistics:")
            print(f"- Total unique tweets: {len(unique_tweets)}")
            print(f"- Unique users: {user_count}")
            print(f"- Total likes: {likes_count}")
            print(f"- Total retweets: {retweets_count}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    
    finally:
        # Always close the browser
        scraper.close()
        print("\nScraping completed. Browser closed.")

if __name__ == "__main__":
    print("Starting Twitter scraper for Uber research...")
    main()