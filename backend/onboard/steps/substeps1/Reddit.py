import praw
import pandas as pd
import json

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id="qApJC9H-Od2AJU0eQJN84g",  # your client id
    client_secret="19zsvlAHsCJMNithtcHUg0jI9Y4f3A",  # your client secret
    user_agent="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 9_4_2) AppleWebKit/601.24 (KHTML, like Gecko) Chrome/50.0.1832.351 Safari/603"
    # your user agent
)

# Set batch size and initialize variables
batch_size = 1000
batch_number = 1
posts_list = []
total_posts = 0

# Fetch submissions from the "uber" subreddit, sorted by new
for submission in reddit.subreddit("uber").new(limit=None):
    # Extract post data into a dictionary
    post_data = {
        "title": submission.title,
        "rating": submission.score,
        "review_id": submission.id,
        "url": submission.url,
        "date": submission.created_utc,  # Unix timestamp (UTC)
        "review": submission.selftext,
        "username": str(submission.author) if submission.author else None,
    }

    # Fetch all comments for the submission
    submission.comments.replace_more(limit=None)  # Fetch all comments, including "MoreComments"
    comments = [comment.body for comment in submission.comments.list()]
    post_data["comments"] = json.dumps(comments)  # Store comments as a JSON string

    # Add post data to the current batch
    posts_list.append(post_data)
    total_posts += 1

    # When batch reaches 1000 posts, save to CSV
    if len(posts_list) == batch_size:
        df = pd.DataFrame(posts_list)
        df.to_csv(f"uber_posts_{batch_number}.csv", index=False, encoding='utf-8')
        print(f"Saved batch {batch_number} with {batch_size} posts. Total posts: {total_posts}")
        batch_number += 1
        posts_list = []  # Clear the list for the next batch

# Save any remaining posts (less than 1000) after the loop
if posts_list:
    df = pd.DataFrame(posts_list)
    df.to_csv(f"uber_posts_{batch_number}.csv", index=False, encoding='utf-8')
    print(f"Saved final batch {batch_number} with {len(posts_list)} posts. Total posts: {total_posts}")