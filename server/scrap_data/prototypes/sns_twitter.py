import pandas as pd
from ntscraper import Nitter
import logging

# Configure logging to display info-level messages
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_tweets_data(scraper, query, mode, number=1000):
    """
    Scrape tweets using the specified query and mode.
    Mode can be 'term' (tweets containing the query) or 'hashtag'.
    """
    try:
        logging.info(f"Fetching tweets for query='{query}' in mode='{mode}'...")
        result = scraper.get_tweets(query, mode=mode, number=number)
        tweets = result.get('tweets', [])
        logging.info(f"Retrieved {len(tweets)} tweets for mode='{mode}'")
        return tweets
    except Exception as e:
        logging.error(f"Error fetching tweets in mode '{mode}': {e}")
        return []

def remove_duplicates(tweets):
    """
    Remove duplicate tweets based on a unique identifier.
    We try using the tweet's 'tweet_id' if available, or fallback to the 'link'.
    """
    seen = set()
    unique = []
    for tweet in tweets:
        tweet_id = tweet.get('tweet_id') or tweet.get('link')
        if tweet_id and tweet_id not in seen:
            seen.add(tweet_id)
            unique.append(tweet)
    return unique

def collect_all_tweets(company, number=1000):
    """
    Use multiple modes to collect tweets related to the company.
    """
    # Initialize the scraper
    scraper = Nitter(log_level=1, skip_instance_check=False)
    
    # Fetch tweets using both term and hashtag searches.
    term_tweets = get_tweets_data(scraper, company, mode='term', number=number)
    hashtag_tweets = get_tweets_data(scraper, company, mode='hashtag', number=number)
    
    # Combine the tweets and remove duplicates.
    all_tweets = term_tweets + hashtag_tweets
    unique_tweets = remove_duplicates(all_tweets)
    logging.info(f"Total unique tweets collected: {len(unique_tweets)}")
    return unique_tweets

def tweets_to_dataframe(tweets):
    """
    Extract selected fields from the tweet data and convert to a DataFrame.
    """
    data = []
    for tweet in tweets:
        text = tweet.get('text', '')
        date = tweet.get('date', '')
        link = tweet.get('link', '')
        stats = tweet.get('stats', {})
        likes = stats.get('likes')
        comments = stats.get('comments')
        retweets = stats.get('retweets')
        data.append({
            "text": text,
            "date": date,
            "link": link,
            "likes": likes,
            "comments": comments,
            "retweets": retweets,
        })
    df = pd.DataFrame(data)
    return df

def main():
    # Hardcoded company: Netflix
    company = "Amazon"
    number = 1000  # Number of tweets to fetch per mode

    # Collect tweets related to Netflix using both search modes
    tweets = collect_all_tweets(company, number=number)
    if not tweets:
        logging.error("No tweets were collected. Exiting.")
        return

    # Convert the tweets into a pandas DataFrame
    df = tweets_to_dataframe(tweets)
    
    # Save the results to a CSV file
    output_file = f"{company}_tweets.csv"
    df.to_csv(output_file, index=False)
    logging.info(f"Saved {len(df)} tweets to {output_file}")

if __name__ == "__main__":
    main()
