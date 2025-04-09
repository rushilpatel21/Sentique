from django.core.management.base import BaseCommand
from django.db import transaction
from reviews.models import Review
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 100

# Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings_for_texts(texts):
    """
    Generates embeddings for a list of texts using SentenceTransformer.
    Returns a list of 384-dimensional float vectors (one per text).
    """
    # Generate embeddings; this returns a numpy array.
    embeddings = model.encode(texts, show_progress_bar=False)
    # Convert each embedding to a list of floats.
    return [embedding.tolist() for embedding in embeddings]

class Command(BaseCommand):
    """
    Usage:
      python manage.py generate_review_embeddings
    """
    help = "Generate and store vector embeddings using SentenceTransformer for Reviews missing embeddings."

    def handle(self, *args, **options):
        # 1. Find all Reviews that have null embeddings.
        queryset = Review.objects.filter(embedding__isnull=True)
        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No reviews found with null embeddings."))
            return

        self.stdout.write(f"Found {total} reviews without embeddings.")

        start_index = 0

        while True:
            # 2. Fetch a batch of up to CHUNK_SIZE reviews.
            reviews_batch = list(queryset[start_index:start_index + CHUNK_SIZE])
            if not reviews_batch:
                break

            texts = [rev.review for rev in reviews_batch]  # Embed the review text.
            batch_size = len(texts)
            self.stdout.write(
                f"Processing batch of {batch_size} reviews "
                f"(index {start_index} to {start_index + batch_size - 1})"
            )

            # 3. Generate embeddings using SentenceTransformer.
            embeddings = get_embeddings_for_texts(texts)

            # 4. Assign the embeddings to the Review objects.
            for review_obj, emb_vector in zip(reviews_batch, embeddings):
                review_obj.embedding = emb_vector  # VectorField accepts a list of floats.

            # 5. Bulk update to store embeddings in the database.
            with transaction.atomic():
                Review.objects.bulk_update(reviews_batch, ['embedding'])

            start_index += CHUNK_SIZE

        self.stdout.write(self.style.SUCCESS("Embedding generation completed!"))
