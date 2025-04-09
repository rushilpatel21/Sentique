from sentence_transformers import SentenceTransformer
from reviews.models import Review
from django.db import transaction

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to get embedding for a given review text
def get_embedding(text):
    # Generate the embedding as a list of floats
    return model.encode(text).tolist()

# Function to process and update embeddings in batches
def generate_and_store_embeddings_batch(batch_size=500):
    reviews = Review.objects.all()  # Retrieve all reviews from the database
    total_reviews = reviews.count()

    with transaction.atomic():
        for start in range(0, total_reviews, batch_size):
            # Fetch a batch of reviews
            batch_reviews = reviews[start:start + batch_size]
            for review in batch_reviews:
                # Generate embedding for each review
                embedding = get_embedding(review.review)

                # Store the embedding list directly in JSONField
                review.embedding = embedding
                review.save()

# Run the embedding generation and storing process with batching
generate_and_store_embeddings_batch(batch_size=500)

print("Embeddings have been successfully generated and stored in the database.")