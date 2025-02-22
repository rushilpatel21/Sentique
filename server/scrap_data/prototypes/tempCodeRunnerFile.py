from ntscraper import Nitter

scraper = Nitter(log_level=1, skip_instance_check=False)

netflix_hash_tweets = scraper.get_tweets("Netflix", mode='hashtag')

# only print the first 5 tweets content

for tweet in netflix_hash_tweets[:5]:
    print(tweet['text'])
