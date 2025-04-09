from django.contrib.postgres.fields import ArrayField
from django.db import models
from onboard.models import UserData
from pgvector.django import VectorField


class Review(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="reviews")
    review_id = models.CharField(max_length=100, unique=True)  # Custom ID from source
    date = models.DateTimeField()
    rating = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=200)
    review = models.TextField()
    title = models.CharField(max_length=500, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=500)
    comments = models.JSONField(default=list)  # Array of comments as JSON
    language = models.CharField(max_length=50, null=True, blank=True)


    category = models.CharField(max_length=100, null=True, blank=True)
    sub_category = models.CharField(max_length=100, null=True, blank=True)
    sentiment = models.CharField(
        max_length=20,
        choices=[("positive", "Positive"), ("negative", "Negative"), ("neutral", "Neutral")],
        null=True,
        blank=True
    )
    particular_issue = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    embedding = VectorField(dimensions=384, null=True, blank=True, default=None)


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_data', 'review_id']),
        ]