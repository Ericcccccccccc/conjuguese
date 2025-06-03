import json
import os
import google.generativeai as genai
from ..config import GOOGLE_API_KEY # Import API key from config

# Configure Gemini API (should be done in config, but ensure it's configured if this service is used directly)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_feedback_from_gemini(sentences_to_evaluate):
    """
    Sends sentences to Gemini API for feedback and returns structured feedback.
    sentences_to_evaluate: A list of strings, where each string is a sentence.
    """
    if not GOOGLE_API_KEY:
        print("Error: Gemini API key not configured. Skipping feedback.")
        # Return a default feedback structure indicating an error or no feedback, along with debug info
        return {
            "feedback_list": [{"gemini_feedback": {"error": "API key not configured"}, "original_sentence": s} for s in sentences_to_evaluate],
            "debug_info": {
                "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                "prompt_sent": "API key not configured, no prompt sent.",
                "raw_response": "API key not configured, no response received.",
                "error": "API key not configured."
            }
        }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-04-17",
        generation_config={"response_mime_type": "application/json"}
    )

    # Prepare the prompt for Gemini
    prompt_parts = [
        "You are an expert Portuguese language tutor. Evaluate the following Portuguese sentences submitted by a student.",
        "Your response MUST be a single, valid JSON array. Each element in the array must be a JSON object corresponding to one input sentence, maintaining the original order.",
        "\nEach JSON object must strictly follow this structure:",
        "\nFor a sentence identified as Portuguese:",
        """
```json
{
  "original_sentence_index": "0",  // String: 0-based index
  "is_portuguese": true,
  "feedback": {
    "grammar_analysis": "Detailed grammar feedback. Point out specific errors and explain them. If correct, acknowledge. Ensure all special characters within this string are properly escaped (e.g., \\\\\\\" for quotes, \\\\\\\\ for backslash, \\\\n for newlines).",
    "spelling_errors": [
      { "error": "misspelled_word", "correction": "corrected_word" }
      // This array can be empty [] if no spelling errors.
    ],
    "naturalness_evaluation": "Comment on how natural the sentence sounds (e.g., 'Sounds natural', 'A bit formal', 'Sounds awkward because...'). Properly escape special characters.",
    "suggestions": [
      "Suggestion 1 for improvement or alternative phrasing. Properly escape special characters.",
      "Another suggestion if applicable. Properly escape special characters."
      // This array can be empty [] if no suggestions.
    ]
  },
  "overall_comment": "A brief overall comment or encouragement. Properly escape special characters."
}
```""",
        "\nFor a sentence NOT identified as Portuguese (or nonsensical):",
        """
```json
{
  "original_sentence_index": "1", // String: 0-based index
  "is_portuguese": false,
  "feedback": null, # Note: the value is null (the JSON null literal), not the string "null"
  "overall_comment": "This does not appear to be a Portuguese sentence. Or, explain why it's nonsensical. Properly escape special characters."
}
```""",
        "\nKey requirements for the JSON:",
        "- The entire output must be a single JSON array `[ ... ]`.",
        "- All property names (keys) MUST be enclosed in double quotes (e.g., `\"feedback\"`).",
        "- All string values MUST be enclosed in double quotes and properly escaped (e.g., `\"content with a \\\\\\\"quote\\\\\\\"\"`).",
        "- `feedback` should be `null` (the JSON null literal) if `is_portuguese` is `false`.",
        "- Ensure no trailing commas in objects or arrays.",
        "\nHere are the sentences to evaluate:"
    ]

    # Add each sentence to the prompt, clearly indexed for the LLM
    for i, sentence_text in enumerate(sentences_to_evaluate):
        prompt_parts.append(f"Sentence {i}: \"{sentence_text}\"")

    full_prompt = "\n".join(prompt_parts)

    try:
        print(f"Sending prompt to Gemini: {full_prompt[:500]}...") # Log a snippet of the prompt

        try:
            response = model.generate_content(full_prompt)
            # Debug: Print raw response text
            print(f"Gemini raw response: {response.text}")
            response_text = response.text
        except Exception as api_call_error:
            print(f"Error during Gemini API call or accessing response text: {api_call_error}")
            # Return an error structure indicating the API call failed
            return {
                "feedback_list": [{"gemini_feedback": {"error": f"API call failed: {api_call_error}"}, "original_sentence": s} for s in sentences_to_evaluate],
                "debug_info": {
                    "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                    "prompt_sent": full_prompt,
                    "raw_response": None, # No response text on API call error
                    "error": str(api_call_error)
                }
            }

        # The response_text should be a JSON string if response_mime_type worked.
        feedback_list = json.loads(response_text)

        # Ensure the feedback_list is indeed a list and has the correct length
        if not isinstance(feedback_list, list) or len(feedback_list) != len(sentences_to_evaluate):
            print(f"Error: Gemini response is not a list or length mismatch. Got: {feedback_list}")
            # Fallback: return error feedback for each sentence
            return {
                "feedback_list": [{"gemini_feedback": {"error": "Invalid response format from API"}, "original_sentence": s} for s in sentences_to_evaluate],
                 "debug_info": {
                    "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                    "prompt_sent": full_prompt,
                    "raw_response": response_text,
                    "error": "Invalid response format from API."
                }
            }

        # Map feedback to original sentences based on index or order
        # Assuming Gemini returns feedback in the same order as sentences were provided
        # and includes original_sentence_index if we need more robust mapping.
        # For now, we rely on order.

        processed_feedback = []
        for i, fb in enumerate(feedback_list):
            # We expect 'fb' to be the structured feedback object.
            # We'll add the original sentence text back for convenience if needed later,
            # though the template will get it from the main sentence object.
            processed_feedback.append({
                "gemini_feedback": fb, # This is the JSON object from Gemini
                "original_sentence": sentences_to_evaluate[i] # Keep original for reference if needed
            })
        return {
            "feedback_list": processed_feedback,
            "debug_info": {
                "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                "prompt_sent": full_prompt,
                "raw_response": response_text,
                "error": None
            }
        }

    except json.JSONDecodeError as json_error:
        print(f"Error parsing Gemini JSON response: {json_error}. Attempting to extract JSON.")
        # Attempt to extract JSON from the raw response text
        extracted_json_text = None
        try:
            start_index = response_text.find('[')
            end_index = response_text.rfind(']')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                extracted_json_text = response_text[start_index : end_index + 1]
                feedback_list = json.loads(extracted_json_text)
                print("Successfully extracted and parsed JSON.")
                 # Ensure the feedback_list is indeed a list and has the correct length
                if not isinstance(feedback_list, list) or len(feedback_list) != len(sentences_to_evaluate):
                    print(f"Error: Extracted Gemini response is not a list or length mismatch. Got: {feedback_list}")
                    raise ValueError("Extracted JSON has invalid format or length.") # Raise to be caught by the outer except

                processed_feedback = []
                for i, fb in enumerate(feedback_list):
                    processed_feedback.append({
                        "gemini_feedback": fb,
                        "original_sentence": sentences_to_evaluate[i]
                    })
                return {
                    "feedback_list": processed_feedback,
                    "debug_info": {
                        "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                        "prompt_sent": full_prompt,
                        "raw_response": response_text if 'response_text' in locals() else None, # Include raw response if available
                        "error": "JSON extracted and parsed successfully after initial error."
                    }
                }

            else:
                print("Could not extract valid JSON from response.")
                raise ValueError("Could not extract valid JSON from response.") # Raise to be caught by the outer except

        except Exception as extraction_error:
            print(f"Error during JSON extraction or parsing of extracted text: {extraction_error}")
            # Return a default error structure for each sentence, along with debug info
            return {
                "feedback_list": [{"gemini_feedback": {"error": f"JSON parsing and extraction error: {json_error}, Extraction error: {extraction_error}"}, "original_sentence": s} for s in sentences_to_evaluate],
                "debug_info": {
                    "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                    "prompt_sent": full_prompt,
                    "raw_response": response_text if 'response_text' in locals() else None, # Include raw response if available
                    "error": f"JSON parsing error: {json_error}, Extraction error: {extraction_error}"
                }
            }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Catch any other unexpected errors
        return {
            "feedback_list": [{"gemini_feedback": {"error": f"Unexpected error: {e}"}, "original_sentence": s} for s in sentences_to_evaluate],
            "debug_info": {
                "api_key_masked": GOOGLE_API_KEY[:4] + "..." if GOOGLE_API_KEY else "None",
                "prompt_sent": full_prompt,
                "raw_response": response_text if 'response_text' in locals() else None, # Include raw response if available
                "error": str(e)
            }
        }
