# backend/views.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import StreamingHttpResponse
import json
import time
import random

from reviews.models import Review
from django.db.models import F
from django.db.models.expressions import RawSQL
from sentence_transformers import SentenceTransformer

# Use the same Gemini import as trends analysis
import google.generativeai as genai
from environs import env
import re
import datetime
from django.utils.timezone import now

# Load environment variables - use same configuration as trends analysis
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully for chat.")
else:
    print("Warning: GEMINI_API_KEY not found in environment variables.")  


def retry_with_exponential_backoff(func, max_retries=3, base_delay=1):
    """
    Retry a function with exponential backoff on rate limit errors.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit, retrying in {delay:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise e  


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
    if not reviews:
        return "No relevant reviews found in the database."
    
    context_list = []
    for i, rev in enumerate(reviews[:10]):  # Limit to top 10 reviews to avoid token limits
        snippet = rev.review[:300] if rev.review else "No review text available"  # Truncate review text to 300 characters
        context_list.append(
            f"Review {i+1}:\nRating: {rev.rating}/5\nSentiment: {rev.sentiment}\nDate: {rev.date}\nReview: {snippet}..."
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
            print(f"Total reviews with embeddings: {qs.count()}")
            
            if 'sentiment' in filters:
                qs = qs.filter(sentiment=filters['sentiment'])
                print(f"Reviews after sentiment filter ({filters['sentiment']}): {qs.count()}")

            # Use RawSQL to compute the vector distance, casting the parameter to vector.
            qs = qs.annotate(
                distance=RawSQL("embedding <-> %s::vector", (formatted_query,))
            ).order_by("distance")
            top_reviews = list(qs[:20])  # Retrieve top 20 closest reviews (was 200, then only 5 used)
            print(f"Retrieved {len(top_reviews)} reviews for context")
            
            # If no reviews found with vector similarity, try getting recent reviews as fallback
            if not top_reviews:
                print("No vector similarity results found, trying fallback query...")
                fallback_qs = Review.objects.filter(review__isnull=False).exclude(review='')
                if 'sentiment' in filters:
                    fallback_qs = fallback_qs.filter(sentiment=filters['sentiment'])
                top_reviews = list(fallback_qs.order_by('-date')[:20])
                print(f"Fallback query retrieved {len(top_reviews)} reviews")

            # 4. Build a context string from the retrieved reviews.
            context_str = build_context_from_reviews(top_reviews)
            print(f"Context string length: {len(context_str)} characters")

            # 5. Construct the prompt for Gemini - use same format as trends analysis
            if not top_reviews:
                final_prompt = f"""
You are an AI assistant for Uber ride analysis. The user asked: "{user_query}"

Unfortunately, no relevant reviews were found in the database to answer this specific question. 
This could be because:
1. There are no reviews with embeddings in the database
2. The reviews don't match the current filters
3. The vector similarity search didn't find relevant matches

Please provide a general response about Uber rides based on your knowledge, but mention that specific user review data is not available to support the answer.
"""
            else:
                final_prompt = f"""
You are an AI assistant analyzing Uber reviews. Below are some relevant reviews:

{context_str}

User Question: {user_query}

Use these reviews to provide an insightful answer to the user's question. 
If the reviews do not provide enough information, indicate uncertainty.
Keep your response concise and helpful.
"""

            # 6. Call Gemini using the same method as trends analysis
            try:
                def make_gemini_call():
                    # Use the same model and configuration as trends analysis
                    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
                    response = model.generate_content(final_prompt)
                    return response
                
                # Use retry logic for the API call
                response = retry_with_exponential_backoff(make_gemini_call)

                # Since we're using the same non-streaming API as trends analysis,
                # we need to handle the response differently
                def stream_to_client():
                    try:
                        # Get the response text using the same method as trends analysis
                        if hasattr(response, 'text'):
                            response_text = response.text
                        else:
                            # For newer API versions, use the parts accessor
                            response_text = response.candidates[0].content.parts[0].text
                        
                        # Stream the response in chunks to simulate streaming
                        chunk_size = 50  # characters per chunk
                        for i in range(0, len(response_text), chunk_size):
                            chunk = response_text[i:i + chunk_size]
                            yield f'0:{json.dumps(chunk)}\n'
                            time.sleep(0.05)  # Small delay to simulate streaming
                        
                    except Exception as e:
                        if "429" in str(e) or "Too Many Requests" in str(e):
                            yield f'0:{json.dumps("Rate limit exceeded. Please try again in a few moments.")}\n'
                        else:
                            yield f'0:{json.dumps(f"Error generating response: {str(e)}")}\n'

                return StreamingHttpResponse(stream_to_client(), content_type="text/event-stream")
            
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    return Response(
                        {"error": "Rate limit exceeded. Please try again in a few moments."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
                else:
                    raise e

        except Exception as e:
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
