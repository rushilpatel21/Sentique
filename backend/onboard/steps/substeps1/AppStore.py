import pandas as pd
import numpy as np
from app_store_scraper import AppStore
import datetime
import os


def scrape_app_reviews(app_name, app_id, country='us', total_reviews=100000, batch_size=1000):
    # Initialize the AppStore scraper
    app = AppStore(country=country, app_name=app_name, app_id=app_id)

    # Create directory for CSV files if it doesn't exist
    output_dir = f'{app_name}_reviews'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_reviews = []
    reviews_collected = 0
    file_counter = 1

    while reviews_collected < total_reviews:
        # Calculate how many reviews to fetch in this batch
        remaining = total_reviews - reviews_collected
        fetch_count = min(batch_size, remaining)

        try:
            # Fetch reviews
            app.review(how_many=fetch_count)

            # Process reviews into desired schema
            for review in app.reviews:
                formatted_review = {
                    "date": review.get('date', datetime.datetime.now()),
                    "rating": review.get('rating', 0),
                    "review": review.get('review', ''),
                    "title": review.get('title', ''),
                    "username": review.get('userName', ''),
                    "source": "appstore",
                }
                all_reviews.append(formatted_review)

            reviews_collected += len(app.reviews)
            print(f"Collected {reviews_collected} reviews so far...")

            # Save to CSV after every batch_size reviews
            if len(all_reviews) >= batch_size or reviews_collected >= total_reviews:
                df = pd.DataFrame(all_reviews)
                filename = f'{output_dir}/{app_name}_reviews_{file_counter}.csv'
                df.to_csv(filename, index=False)
                print(f"Saved {len(all_reviews)} reviews to {filename}")

                # Clear the list and increment counter
                all_reviews = []
                file_counter += 1

            # Clear the reviews from the app object to prevent memory issues
            app.reviews = []

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break

    # Save any remaining reviews
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        filename = f'{output_dir}/{app_name}_reviews_{file_counter}.csv'
        df.to_csv(filename, index=False)
        print(f"Saved final {len(all_reviews)} reviews to {filename}")

    print(f"Scraping completed. Total reviews collected: {reviews_collected}")


# Example usage for Uber
if __name__ == "__main__":
    scrape_app_reviews(
        app_name='uber-request-a-ride',
        app_id='368677368',
        country='us',
        total_reviews=100000,
        batch_size=1000
    )