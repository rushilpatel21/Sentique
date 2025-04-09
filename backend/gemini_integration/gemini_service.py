import os
import google.generativeai as genai
from typing import List, Dict, Any

# Configure the Gemini API with your key
# Make sure to set GEMINI_API_KEY in your environment variables or .env file
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_analysis(reviews: List[str], category: str, date: str) -> Dict[str, Any]:
    """
    Generate analysis of reviews using Google's Gemini API
    
    Args:
        reviews: List of review texts
        category: Category of the reviews
        date: Date string for context
        
    Returns:
        Dictionary with analysis results containing pros and cons
    """
    # If no reviews were found
    if not reviews:
        return {
            "pros": ["No positive feedback found in the selected date range."],
            "cons": ["No negative feedback found in the selected date range."]
        }
    
    # Only use up to 20 reviews to avoid token limits
    reviews_text = "\n".join(reviews[:20])
    
    # Create the prompt for Gemini
    prompt = f"""
Based *only* on the following user reviews for category '{category}' around {date}:

{reviews_text}

Please summarize the main pros (positive points) and cons (negative points) mentioned. 
Format your response as a JSON object with two arrays: "pros" and "cons".
Each array should contain 3-7 distinct points mentioned in the reviews.
For example:
{{
    "pros": ["Point 1", "Point 2", ...],
    "cons": ["Issue 1", "Issue 2", ...]
}}
"""

    try:
        # Initialize the model
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        
        # Generate the response
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        import json
        try:
            # The response might be in a code block format, so we need to extract it
            response_text = response.text
            if "```json" in response_text:
                # Extract JSON from code block
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                json_str = response_text[json_start:json_end].strip()
                result = json.loads(json_str)
            else:
                # Try to parse the raw text
                result = json.loads(response_text)
                
            # Ensure we have both pros and cons
            if "pros" not in result or "cons" not in result:
                raise ValueError("Response missing pros or cons")
                
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, we'll manually extract pros and cons
            response_text = response.text
            pros = []
            cons = []
            
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if "pros" in line.lower() or "positive" in line.lower():
                    current_section = "pros"
                    continue
                elif "cons" in line.lower() or "negative" in line.lower():
                    current_section = "cons"
                    continue
                
                if not line or ":" in line or not current_section:
                    continue
                    
                if line.startswith("- ") or line.startswith("* "):
                    point = line[2:].strip()
                    if current_section == "pros":
                        pros.append(point)
                    else:
                        cons.append(point)
            
            return {
                "pros": pros if pros else ["Positive aspects could not be extracted clearly."],
                "cons": cons if cons else ["Negative aspects could not be extracted clearly."]
            }
    
    except Exception as e:
        print(f"Error generating analysis with Gemini: {str(e)}")
        return {
            "pros": ["Analysis generation failed. Please try again."],
            "cons": ["Analysis generation failed. Please try again."],
            "error": str(e)
        }