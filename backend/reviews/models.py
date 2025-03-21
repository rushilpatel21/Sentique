import uuid  # Importing the UUID module to generate unique identifiers
from django.db import models  # Importing Django's models module

class Review(models.Model):
    """
    This model represents a user-submitted review.
    It captures the review details, the platform it was submitted on, and its classification.
    """

    # 1. Unique identifier for each review.
    #    - Uses UUID (Universally Unique Identifier) instead of an auto-incrementing integer.
    #    - Ensures uniqueness across distributed systems.
    #    - `editable=False` prevents users from modifying the ID.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 2. Defining predefined choices for the 'category' field.
    #    - Ensures consistency in classification.
    #    - Prevents incorrect or free-text inputs.
    CATEGORY_CHOICES = [
        ('improvement', 'Improvement'),  # Feedback suggesting improvements
        ('complaint', 'Complaint'),  # Negative feedback or reported issues
        ('praise', 'Praise'),  # Positive feedback or compliments
    ]

    # 3. Timestamp for when the review is created.
    #    - `auto_now_add=True`: Automatically sets the field to the current timestamp when a new record is created.
    #    - `db_index=True`: Indexing improves performance when filtering reviews by date.
    date = models.DateTimeField(auto_now_add=True, db_index=True)

    # 4. The main review text provided by the user.
    #    - `TextField` is used to store large amounts of text without a character limit.
    review = models.TextField()

    # 5. Optional field to store a URL related to the review.
    #    - `max_length=500`: Limits URL length to 500 characters.
    #    - `blank=True`: Allows this field to be left empty.
    #    - `null=True`: Stores NULL in the database if no URL is provided.
    review_url = models.URLField(max_length=500, blank=True, null=True)

    # 6. The platform where the review was posted.
    #    - Example: 'Amazon', 'Google Reviews', 'Yelp'
    #    - `max_length=100`: Restricts the platform name length.
    #    - `db_index=True`: Speeds up queries filtering by platform.
    platform = models.CharField(max_length=100, db_index=True)

    # 7. General classification of the review.
    #    - Example: 'Product Quality', 'Customer Service', 'Delivery'
    #    - Helps in categorizing reviews at a high level.
    #    - `db_index=True`: Optimizes queries filtering by general category.
    general_category = models.CharField(max_length=200, db_index=True)

    # 8. More detailed classification within the general category.
    #    - Example: If 'Product Quality' is the general category, 'Build Quality' can be a specific category.
    #    - `db_index=True`: Allows quick lookups based on this classification.
    specific_category = models.CharField(max_length=200, db_index=True)

    # 9. Explanation of why the review falls under the given classification.
    #    - Helps in understanding the reasoning behind the category selection.
    reason = models.TextField()

    # 10. The primary category of the review.
    #     - Limited to predefined values using `CATEGORY_CHOICES`.
    #     - `db_index=True`: Enhances query performance when filtering by category.
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)

    # 11. String representation of the model.
    #     - Defines how an instance of this model appears in Django Admin or when printed.
    #     - Displays the platform name, review category, and date for better readability.
    def __str__(self):
        return f"{self.platform} - {self.category} - {self.date}"
