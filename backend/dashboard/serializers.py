from rest_framework import serializers
from reviews.models import Review
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'review_id', 'date', 'rating', 'source', 'review', 'title', 'username', 'url', 'category', 'sub_category', 'sentiment', 'particular_issue', 'summary']
