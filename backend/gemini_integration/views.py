# backend/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import StreamingHttpResponse
import json

from reviews.models import Review
from django.db.models import F
from django.db.models.expressions import RawSQL
from sentence_transformers import SentenceTransformer

from google import genai
from environs import env
import re
import datetime
from django.utils.timezone import now

env.read_env()
client = genai.Client(api_key="AIzaSyDdY5zm6vURga8LZvuOGXLAMJOjqjbClLE")  # Replace with your actual key


def extract_filters_from_prompt(prompt):
    """
    Naively extract filters (e.g., sentiment) from the user prompt.
    Extend this function for more robust extraction if needed.
    """
    filters = {}
    prompt_lower = prompt.lower()
    if 'negative' in prompt_lower:
        filters['sentiment'] = 'negative'
    elif 'positive' in prompt_lower:
        filters['sentiment'] = 'positive'
    elif 'neutral' in prompt_lower:
        filters['sentiment'] = 'neutral'
    return filters


def build_context_from_reviews(reviews):
    """
    Build a context string from a list of Review objects.
    """
    context_list = []
    for rev in reviews:
        snippet = rev.review[:300]  # Truncate review text to 300 characters
        context_list.append(
            f"Review ID: {rev.review_id}\nRating: {rev.rating}\nSentiment: {rev.sentiment}\nDate: {rev.date}\nReview: {snippet}..."
        )
    return "\n\n".join(context_list)


def format_vector(vector):
    """
    Format a Python list of floats as a PostgreSQL vector literal, e.g., "[0.1,0.2,...]".
    """
    return "[" + ",".join(map(str, vector)) + "]"


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            messages = data.get('messages', [])
            if not messages:
                return Response({"error": "No messages provided."}, status=400)

            # Use the last message as the user's query.
            user_query = messages[-1]['content']

            # 1. Extract filters from the query (e.g., sentiment)
            filters = extract_filters_from_prompt(user_query)

            # 2. Embed the query using SentenceTransformer.
            # "all-MiniLM-L6-v2" produces 384-dimensional embeddings.
            st_model = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = st_model.encode([user_query])[0].tolist()
            formatted_query = format_vector(query_embedding)

            # 3. Retrieve relevant reviews using vector similarity.
            qs = Review.objects.filter(embedding__isnull=False)
            if 'sentiment' in filters:
                qs = qs.filter(sentiment=filters['sentiment'])

            # Use RawSQL to compute the vector distance, casting the parameter to vector.
            qs = qs.annotate(
                distance=RawSQL("embedding <-> %s::vector", (formatted_query,))
            ).order_by("distance")
            top_reviews = list(qs[:200])  # Retrieve the top 5 closest reviews

            # 4. Build a context string from the retrieved reviews.
            context_str = build_context_from_reviews(top_reviews)

            # 5. Construct the prompt for Gemini.
            system_message = (
                "You are an AI assistant analyzing Uber reviews. Below are some relevant reviews:\n\n"
                f"{context_str}\n\n"
                "Use these reviews to provide an insightful answer to the user's question. "
                "If the reviews do not provide enough information, indicate uncertainty."
            )
            final_prompt = [
                {
                    "role": "model",
                    "parts": [{"text": system_message}]
                },
                {
                    "role": "user",
                    "parts": [{"text": user_query}]
                }
            ]

            # 6. Call Gemini to generate a response and stream it back.
            response = client.models.generate_content_stream(
                model="gemini-1.5-pro",
                contents=final_prompt,
            )

            def stream_to_client():
                for chunk in response:
                    text = chunk.text
                    yield f'0:{json.dumps(text)}\n'

            return StreamingHttpResponse(stream_to_client(), content_type="text/event-stream")

        except Exception as e:
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
