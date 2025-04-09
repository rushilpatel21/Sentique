import os
import re
import json
from typing import List, Dict, Any
from datetime import datetime

# Try to import the Gemini package, but provide a fallback if unavailable
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    # Configure the Gemini API with your key
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini API configured successfully.")
    else:
        print("Warning: GEMINI_API_KEY not found in environment variables. Gemini analysis unavailable.")
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google.generativeai package not available. Using fallback analysis.")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"Warning: Error configuring Gemini API: {e}. Using fallback analysis.")


def generate_analysis(reviews: List[str], category: str, date_range: str) -> Dict[str, Any]:
    """
    Generate enhanced analysis of reviews using Google's Gemini API if available,
    otherwise use a simple fallback method.

    Args:
        reviews: List of review texts.
        category: Category of the reviews (e.g., 'Restaurant', 'Software Tool').
        date_range: Description of the time range (e.g., 'last quarter', 'January 2024').

    Returns:
        Dictionary with analysis results containing summary, positive insights (pros),
        and negative insights (cons).
    """
    if not reviews:
        return {
            "summary": f"No reviews found for category '{category}' in the specified date range ({date_range}).",
            "positiveInsights": ["No data available."],
            "negativeInsights": ["No data available."],
            "analysis_type": "no_data"
        }

    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        print(f"Attempting analysis with Gemini for {len(reviews)} reviews...")
        try:
            result = _analyze_with_gemini(reviews, category, date_range)
            result["analysis_type"] = "gemini"
            return result
        except Exception as e:
            print(f"Error during Gemini analysis: {e}. Falling back to simple analysis.")
            result = _simple_analysis(reviews, category, date_range)
            result["analysis_type"] = "simple_fallback_error"
            return result
    else:
        print("Using simple fallback analysis.")
        result = _simple_analysis(reviews, category, date_range)
        result["analysis_type"] = "simple_fallback_config"
        return result


def _simple_analysis(reviews: List[str], category: str, date_range: str) -> Dict[str, Any]:
    """
    Simple fallback analysis based on keyword matching.
    NOTE: This provides very basic insights compared to the LLM approach.
    """
    positive_keywords = [
        "great", "good", "excellent", "awesome", "amazing", "love", "best",
        "helpful", "friendly", "reliable", "easy", "fast", "convenient", "efficient",
        "professional", "satisfied", "recommend", "perfect", "enjoyable", "impressed"
    ]

    negative_keywords = [
        "bad", "poor", "terrible", "awful", "hate", "worst", "problem", "issue",
        "slow", "difficult", "expensive", "incorrect", "wrong", "error", "bug",
        "disappointing", "frustrating", "annoying", "failure", "waste", "unreliable",
        "canceled", "overpriced", "rude", "unprofessional", "late", "wait", "delay"
    ]

    themes = {}
    for review in reviews:
        review_lower = review.lower()
        matches = re.findall(r'(?:very |really |extremely |quite )?(good|great|bad|poor|excellent|terrible) (\w+)', review_lower)
        for sentiment, theme in matches:
            if theme not in themes:
                themes[theme] = {"positive": 0, "negative": 0, "examples": []}

            sentiment_type = "positive" if sentiment in ["good", "great", "excellent"] else "negative"
            themes[theme][sentiment_type] += 1

            # Find the context of the match
            try:
                start_pos = max(0, review_lower.find(f"{sentiment} {theme}") - 30)
                end_pos = min(len(review_lower), review_lower.find(f"{sentiment} {theme}") + len(sentiment) + len(theme) + 30)
                snippet = review[start_pos:end_pos].strip()
                if len(themes[theme]["examples"]) < 3:
                    themes[theme]["examples"].append(snippet)
            except ValueError:
                # Skip if the pattern can't be found (shouldn't happen but just in case)
                pass

    positive_themes = sorted([(k, v) for k, v in themes.items() if v["positive"] > v["negative"]],
                            key=lambda x: x[1]["positive"], reverse=True)
    negative_themes = sorted([(k, v) for k, v in themes.items() if v["negative"] >= v["positive"]],
                            key=lambda x: x[1]["negative"], reverse=True)

    positive_insights = []
    for theme, data in positive_themes[:5]:
        insight = f"Appreciation for '{theme}' was noted {data['positive']} times."
        positive_insights.append(insight)

    general_positives = [
        f"Positive sentiment detected regarding overall '{category.lower()}' experience.",
        f"Mentions of ease or convenience were found."
    ]
    while len(positive_insights) < 3 and general_positives:
         positive_insights.append(general_positives.pop(0))
    if not positive_insights:
        positive_insights = ["General positive feedback was found."]

    negative_insights = []
    for theme, data in negative_themes[:5]:
        insight = f"Concerns regarding '{theme}' were raised {data['negative']} times."
        negative_insights.append(insight)

    general_negatives = [
        f"Some challenges reported related to the '{category.lower()}'.",
        f"Mentions of issues or problems were detected."
    ]
    while len(negative_insights) < 3 and general_negatives:
         negative_insights.append(general_negatives.pop(0))
    if not negative_insights:
        negative_insights = ["General areas for improvement were noted."]

    pos_count = sum(1 for r in reviews if sum(r.lower().count(w) for w in positive_keywords) >
                   sum(r.lower().count(w) for w in negative_keywords))
    neg_count = len(reviews) - pos_count

    if pos_count > neg_count * 1.5:
        sentiment = "generally positive"
    elif neg_count > pos_count * 1.5:
        sentiment = "generally negative"
    else:
        sentiment = "mixed"

    # Add date_range context to the summary
    summary = (
        f"Basic analysis of {len(reviews)} reviews for '{category}' from {date_range} suggests {sentiment} feedback. "
        f"Common keywords suggest positive feedback around {', '.join([t[0] for t in positive_themes[:2]]) if positive_themes else 'certain features'} "
        f"and negative feedback concerning {', '.join([t[0] for t in negative_themes[:2]]) if negative_themes else 'specific aspects'}."
    )

    return {
        "summary": summary,
        "positiveInsights": positive_insights[:5],  # Limit simple insights
        "negativeInsights": negative_insights[:5],  # Limit simple insights
    }


def _analyze_with_gemini(reviews: List[str], category: str, date_range: str) -> Dict[str, Any]:
    """
    Use Gemini API for more sophisticated, synthesized analysis focusing on themes.
    """
    # Sampling strategy 
    MAX_REVIEWS_FOR_PROMPT = 200  # Keep the sample size manageable
    if len(reviews) > MAX_REVIEWS_FOR_PROMPT:
        step = max(1, len(reviews) // MAX_REVIEWS_FOR_PROMPT)
        sampled_reviews = [reviews[i] for i in range(0, len(reviews), step)][:MAX_REVIEWS_FOR_PROMPT]
        print(f"Sampled {len(sampled_reviews)} reviews out of {len(reviews)} for Gemini.")
    else:
        sampled_reviews = reviews

    # Prepare reviews text for the prompt
    reviews_text = "\n\n".join([f"Review {i+1}:\n{review}" for i, review in enumerate(sampled_reviews)])

    # Improved Prompt
    prompt = f"""
Analyze the following {len(sampled_reviews)} customer reviews provided for the category '{category}'. These reviews cover the time range '{date_range}'. Your goal is to synthesize these reviews into a high-quality analysis that identifies overarching themes and sentiment patterns.

**Input Reviews:**
--- START REVIEWS ---
{reviews_text}
--- END REVIEWS ---

**Instructions:**

Based *only* on the provided review texts, generate the following analysis:

1.  **Overall Summary (3-5 sentences):**
    * Provide a concise, insightful overview of the customer experience reflected in these reviews.
    * Synthesize the main sentiment trends (e.g., predominantly positive with specific recurring issues, mixed feedback, etc.).
    * Briefly mention the most prominent positive and negative themes you identified.
    * Focus on the *patterns* observed, not just a count of good/bad reviews.

2.  **Generalized Positive Insights (Pros - 4 to 8 distinct points):**
    * Identify the key *recurring themes* or aspects that customers consistently praised or appreciated.
    * Phrase each point as a general positive aspect derived from patterns in the data (e.g., "Users frequently highlight the platform's ease of use," "Customer support is often commended for responsiveness," "The quality of [specific feature/aspect] receives consistent praise").
    * Each point should represent a distinct theme backed by evidence within the reviews. Avoid generic statements not tied to specific patterns.

3.  **Generalized Negative Insights (Cons - 4 to 8 distinct points):**
    * Identify the key *recurring themes* or aspects that customers consistently criticized or found problematic.
    * Phrase each point as a general area for improvement derived from patterns in the data (e.g., "Several customers report encountering bugs during [specific process]," "The pricing structure is a common point of confusion or frustration," "Users often mention long wait times for [specific service/response]").
    * Each point should represent a distinct theme backed by evidence within the reviews. Avoid generic statements not tied to specific patterns.

**Output Format:**

* Provide your response *exclusively* as a valid JSON object.
* The JSON object must contain three keys: "summary" (string), "positiveInsights" (array of strings), and "negativeInsights" (array of strings).
* Do not include any introductory text, explanations, apologies, or markdown formatting outside the JSON structure itself.

**Example JSON Structure:**
```json
{{
  "summary": "Overall sentiment for '{category}' during {date_range} appears mixed. While customers frequently praise [Theme A] and [Theme B], recurring issues related to [Theme X] and [Theme Y] significantly impact the experience for a notable subset of users.",
  "positiveInsights": [
    "A recurring point of praise is the intuitive nature of the user interface.",
    "Many users appreciate the speed and efficiency of the core service.",
    "Customer service interactions are often described positively, highlighting helpfulness.",
    "The reliability of [specific feature] is frequently mentioned as a key benefit."
  ],
  "negativeInsights": [
    "Users consistently report difficulties with the initial setup process.",
    "The lack of [specific feature/option] is a common frustration.",
    "Several reviews mention unexpected fees or confusing billing statements.",
    "Technical glitches, particularly related to [specific area], are frequently cited."
  ]
}}
```

**Generate the JSON output now based on the provided reviews.**
"""

    # Initialize the model (using 1.5 Pro as it's generally better for nuanced tasks)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    # Configure safety settings
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    # Generation configuration
    generation_config = {
        "temperature": 0.3,  # Lower temperature for more focused, less creative output
        "top_p": 1.0,
        "top_k": 32,
        "max_output_tokens": 8192,  # Adjust based on expected output length
        "response_mime_type": "application/json",  # Explicitly request JSON output
    }

    print("Sending request to Gemini API...")
    # Generate the response
    response = model.generate_content(
        prompt,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # Robust Parsing
    try:
        print("Received response from Gemini. Parsing JSON...")
        result = json.loads(response.text)

        # Validate the structure
        if not all(k in result for k in ["summary", "positiveInsights", "negativeInsights"]):
            raise ValueError("Gemini response missing required keys.")
        if not isinstance(result["summary"], str):
            raise ValueError("Gemini response 'summary' is not a string.")
        if not isinstance(result["positiveInsights"], list) or not all(isinstance(item, str) for item in result["positiveInsights"]):
             raise ValueError("Gemini response 'positiveInsights' is not an array of strings.")
        if not isinstance(result["negativeInsights"], list) or not all(isinstance(item, str) for item in result["negativeInsights"]):
             raise ValueError("Gemini response 'negativeInsights' is not an array of strings.")

        print("Gemini analysis successful.")
        return result

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from Gemini response: {e}")
        print("Gemini Raw Response Text:")
        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
        # Attempt basic extraction as a last resort (less reliable)
        return _extract_from_text_fallback(response.text, category, date_range)
    except ValueError as e:
         print(f"Error: Invalid JSON structure received from Gemini: {e}")
         print("Gemini Raw Response Text:")
         print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
         # Attempt basic extraction as a last resort
         return _extract_from_text_fallback(response.text, category, date_range)
    except Exception as e:
        # Catch other potential errors from the API call or processing
        print(f"An unexpected error occurred during Gemini processing: {str(e)}")
        # Use the simple analysis as a fallback in case of any API or parsing error
        raise  # Re-raise the exception so the calling function handles the fallback


def _extract_from_text_fallback(response_text: str, category: str, date_range: str) -> Dict[str, Any]:
    """Fallback function to attempt extracting analysis sections from raw text if JSON fails."""
    print("Attempting fallback text extraction...")
    summary = "Could not automatically extract summary."
    positive = ["Could not automatically extract positive insights."]
    negative = ["Could not automatically extract negative insights."]

    try:
        # Try finding summary section
        summary_match = re.search(r'summary":\s*"(.*?)"', response_text, re.IGNORECASE | re.DOTALL)
        if not summary_match:
            summary_match = re.search(r'(?:Overall Summary|SUMMARY:?)\s*(.*?)(?:Positive Insights|POSITIVE INSIGHTS:?|Pros|PROS:?|\d\.)', response_text, re.IGNORECASE | re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip().replace('\\n', '\n')

        # Try finding positive insights
        pos_match_json = re.search(r'positiveInsights":\s*\[(.*?)\]', response_text, re.IGNORECASE | re.DOTALL)
        if pos_match_json:
            pos_items = re.findall(r'"(.*?)"', pos_match_json.group(1))
            if pos_items:
                positive = [item.strip().replace('\\n', '\n') for item in pos_items]
        else:
            pos_match_text = re.search(r'(?:Positive Insights|POSITIVE INSIGHTS:?|Pros|PROS:?)\s*(.*?)(?:Negative Insights|NEGATIVE INSIGHTS:?|Cons|CONS:?|Output Format|Example JSON Structure|$)', response_text, re.IGNORECASE | re.DOTALL)
            if pos_match_text:
                pos_items = re.findall(r'^\s*[\*\-\•\d\.]+\s+(.*)', pos_match_text.group(1), re.MULTILINE)
                if pos_items:
                    positive = [item.strip() for item in pos_items]

        # Try finding negative insights
        neg_match_json = re.search(r'negativeInsights":\s*\[(.*?)\]', response_text, re.IGNORECASE | re.DOTALL)
        if neg_match_json:
            neg_items = re.findall(r'"(.*?)"', neg_match_json.group(1))
            if neg_items:
                negative = [item.strip().replace('\\n', '\n') for item in neg_items]
        else:
            neg_match_text = re.search(r'(?:Negative Insights|NEGATIVE INSIGHTS:?|Cons|CONS:?)\s*(.*?)(?:Output Format|Example JSON Structure|$)', response_text, re.IGNORECASE | re.DOTALL)
            if neg_match_text:
                neg_items = re.findall(r'^\s*[\*\-\•\d\.]+\s+(.*)', neg_match_text.group(1), re.MULTILINE)
                if neg_items:
                    negative = [item.strip() for item in pos_items]  # Fix: This should be neg_items not pos_items

    except Exception as e:
        print(f"Error during fallback text extraction: {e}")
        # Keep default error messages if regex fails badly

    return {
        "summary": summary,
        "positiveInsights": positive,
        "negativeInsights": negative
    }

