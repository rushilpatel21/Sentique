import requests
import json
import csv
import time
import os
from datetime import datetime

# API configuration
url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
api_key = "9bc607ac228c4f43b27aec7203fe7bba"
headers = {"X-API-Key": api_key}

# Search parameters - refined to get English tweets containing "uber", excluding retweets
query = "+uber -eats -ubereats -stock -$UBER - lang:en -is:retweet until:2025-01-21	min_faves:10"
query_type = "Top"

# Initialize variables
cursor = " "
all_tweets = []
iteration = 0
max_iterations = 1000  # Set a maximum to avoid infinite loops
csv_every_n_iterations = 10

# Create a timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def save_to_csv(data, iteration_group):
    """Save tweet data to a CSV file"""
    if not data:
        print("No data to save")
        return

    # Create filename with timestamp and iteration group
    filename = f"uber_tweets_en_nort_{timestamp}_batch{iteration_group}.csv"

    # Get the fields from the first tweet to use as headers
    # This assumes all tweets have the same structure
    # Convert the field names in the data
    converted_data = []
    for item in data:
        converted_item = {
            'review_id': item['id'],
            'url': item['url'],
            'review': item['text'],
            'date': item['createdAt'],
            'language': item['lang'],
            'username': item['author.userName']
        }
        converted_data.append(converted_item)

    # Get fieldnames from the converted data
    fieldnames = converted_data[0].keys()

    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(converted_data)

    print(f"Saved {len(data)} English uber tweets (no retweets) to {filename}")


# Main loop to fetch and process tweets
while iteration < max_iterations:
    iteration += 1

    # Set up query parameters with the current cursor
    querystring = {
        "queryType": query_type,
        "query": query,
        "cursor": cursor
    }

    try:
        # Make the API request
        print(f"Iteration {iteration}: Fetching English tweets with 'uber', no retweets (cursor {cursor})")
        response = requests.request("GET", url, headers=headers, params=querystring)

        # Check for successful response
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            break

        # Parse the JSON response
        data = response.json()

        # Extract tweets from the response
        tweets = data.get("tweets", [])

        if not tweets:
            print("No more tweets found or unexpected response structure")
            break

        # Add tweets to our collection
        all_tweets.extend(tweets)
        print(f"Fetched {len(tweets)} tweets. Total collected: {len(all_tweets)}")

        # Get the next cursor from the response
        next_cursor = data.get("next_cursor")

        if not next_cursor or next_cursor == cursor:
            print("No new cursor found or reached the end of results")
            break

        cursor = next_cursor

        # Save to CSV every n iterations
        if iteration % csv_every_n_iterations == 0:
            batch_number = iteration // csv_every_n_iterations
            # Get only the new tweets for this batch
            start_idx = (batch_number - 1) * csv_every_n_iterations
            batch_tweets = all_tweets[start_idx:]
            save_to_csv(batch_tweets, batch_number)

        # Add a small delay to avoid rate limits
        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        break

# Save any remaining tweets
if all_tweets and iteration % csv_every_n_iterations != 0:
    final_batch = iteration // csv_every_n_iterations + 1
    start_idx = (final_batch - 1) * csv_every_n_iterations
    remaining_tweets = all_tweets[start_idx:]
    save_to_csv(remaining_tweets, final_batch)

print(
    f"Completed with {len(all_tweets)} total English 'uber' tweets (no retweets) collected over {iteration} iterations")