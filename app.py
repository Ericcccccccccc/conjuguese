"""
Portuguese Verb Conjugation Practice App
"""

import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from data.verbs import VERBS, TENSE_NAMES, PRONOUNS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env
api_key_loaded = os.getenv('GOOGLE_GEMINI_API_KEY')
if api_key_loaded:
    print(f"DEBUG: GOOGLE_GEMINI_API_KEY found. Length: {len(api_key_loaded)}, Starts with: {api_key_loaded[:4]}, Ends with: {api_key_loaded[-4:]}")
else:
    print("DEBUG: GOOGLE_GEMINI_API_KEY NOT FOUND after load_dotenv().")

app = Flask(__name__)
app.secret_key = 'portuguese_conjugation_app_secret_key'  # Required for session
# Expected environment variable: GOOGLE_GEMINI_API_KEY
app.jinja_env.globals['enumerate'] = enumerate

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("WARNING: GOOGLE_GEMINI_API_KEY not found in environment variables.")
    # You might want to handle this more gracefully, e.g., by disabling Gemini features
    # or raising an error, depending on your application's requirements.

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
SENTENCES_FILE = os.path.join(DATA_DIR, 'sentences.json')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'preferences.json')
SESSION_FILE = os.path.join(DATA_DIR, 'current_session.json')

def ensure_data_files():
    """Ensure all data files exist with proper structure."""
    # Results file
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w') as f:
            json.dump({}, f)
    
    # Sentences file
    if not os.path.exists(SENTENCES_FILE):
        with open(SENTENCES_FILE, 'w') as f:
            json.dump([], f)
    
    # Preferences file
    if not os.path.exists(PREFERENCES_FILE):
        preferences = {verb: {tense: {"never_show": False, "always_show": False} 
                             for tense in VERBS[verb]} 
                      for verb in VERBS}
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f)

ensure_data_files()

def load_results():
    """Load results from the results file."""
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def save_results(results):
    """Save results to the results file."""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f)

def load_sentences():
    """Load sentences from the sentences file."""
    with open(SENTENCES_FILE, 'r') as f:
        return json.load(f)

def save_sentences(sentences):
    """Save sentences to the sentences file."""
    with open(SENTENCES_FILE, 'w') as f:
        json.dump(sentences, f)

def load_preferences():
    """Load preferences from the preferences file."""
    with open(PREFERENCES_FILE, 'r') as f:
        return json.load(f)

def save_preferences(preferences):
    """Save preferences to the preferences file."""
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f)

def get_available_exercises():
    """Get a list of available exercises based on preferences and results."""
    results = load_results()
    preferences = load_preferences()
    available_exercises = []
    
    for verb in VERBS:
        for tense in VERBS[verb]:
            # Skip if marked as "never show"
            if preferences.get(verb, {}).get(tense, {}).get("never_show", False):
                continue
                
            # Check if this conjugation is fully correct
            verb_tense_key = f"{verb}_{tense}"
            if verb_tense_key in results:
                all_correct = all(results[verb_tense_key].get(pronoun, {}).get("correct", False) 
                                 for pronoun in PRONOUNS)
                
                # Skip if all correct and not marked as "always show"
                if all_correct and not preferences.get(verb, {}).get(tense, {}).get("always_show", False):
                    continue
            
            available_exercises.append((verb, tense))
    
    return available_exercises

def select_exercises(count=5):
    """Select a specified number of random exercises."""
    available = get_available_exercises()
    
    # If we have fewer available exercises than requested, use all available
    if len(available) <= count:
        return available
    
    # Otherwise, select random exercises
    return random.sample(available, count)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/start_exercises')
def start_exercises():
    """Start a new set of exercises."""
    exercises = select_exercises(5)
    if not exercises:
        # If no exercises are available, redirect to the main page with a message
        return redirect(url_for('index', message="No exercises available. Please adjust your preferences."))
    
    # Store exercises in session
    session['exercises'] = exercises
    session['current_index'] = 0
    session['errors'] = []
    
    return redirect(url_for('exercise'))

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    """Handle the exercise page."""
    # Check if session exists
    if 'exercises' not in session:
        return redirect(url_for('index', message="Session expired or not found."))
    
    if request.method == 'POST':
        # Process the submitted answers
        current_verb, current_tense = session['exercises'][session['current_index']]
        correct_conjugations = VERBS[current_verb][current_tense]
        
        # Get user answers
        user_answers = [
            request.form.get(f'answer_{i}', '').strip().lower()
            for i in range(4)
        ]
        
        # Check answers
        current_results_list = []
        current_all_correct = True
        for i, (user, correct) in enumerate(zip(user_answers, correct_conjugations)):
            is_correct = user == correct
            if not is_correct:
                current_all_correct = False
                # Add to errors list for sentence practice later
                if 'errors' not in session:
                    session['errors'] = []
                session['errors'].append({
                    'verb': current_verb,
                    'tense': current_tense,
                    'pronoun': PRONOUNS[i],
                    'correct': correct,
                    'user_answer': user
                })
            
            current_results_list.append({
                'pronoun': PRONOUNS[i],
                'user_answer': user,
                'correct_answer': correct,
                'is_correct': is_correct
            })
        
        # Update results file
        update_results(current_verb, current_tense, user_answers)
        
        # Increment index for the next exercise
        session['current_index'] += 1
        
        next_url = ''
        button_text = ''

        if session['current_index'] >= len(session['exercises']):
            # This was the last exercise
            if session.get('errors', []):
                next_url = url_for('sentence_practice')
                button_text = "Praticar Frases"
            else:
                next_url = url_for('clear_session_and_index')
                button_text = "Finalizar"
        else:
            # More exercises remaining
            next_url = url_for('exercise')
            button_text = "Próximo Exercício"
        
        return render_template('results.html', 
                              verb=current_verb, 
                              tense=current_tense, 
                              tense_name=TENSE_NAMES[current_tense],
                              results=current_results_list,
                              all_correct=current_all_correct,
                              next_url=next_url,
                              button_text=button_text)
    
    # GET request - show the current exercise
    # This part handles displaying the exercise page itself or redirecting if all done
    if session['current_index'] >= len(session['exercises']):
        # All exercises completed
        if session.get('errors', []):
            return redirect(url_for('sentence_practice'))
        else:
            # Clear session
            session.pop('exercises', None)
            session.pop('current_index', None)
            session.pop('errors', None)
            return redirect(url_for('index', message="All exercises completed."))
    
    verb, tense = session['exercises'][session['current_index']]
    return render_template('exercise.html', 
                          verb=verb, 
                          tense=tense,
                          tense_name=TENSE_NAMES[tense],
                          pronouns=PRONOUNS,
                          exercise_num=session['current_index'] + 1,
                          total_exercises=len(session['exercises']))

def update_results(verb, tense, user_answers):
    """Update the results file with the latest exercise results."""
    results = load_results()
    verb_tense_key = f"{verb}_{tense}"
    
    if verb_tense_key not in results:
        results[verb_tense_key] = {}
    
    timestamp = datetime.now().isoformat()
    
    for i, pronoun in enumerate(PRONOUNS):
        user_answer = user_answers[i]
        correct_answer = VERBS[verb][tense][i]
        is_correct = user_answer == correct_answer
        
        results[verb_tense_key][pronoun] = {
            "last_answer": user_answer,
            "timestamp": timestamp,
            "correct": is_correct
        }
    
    save_results(results)

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
        model_name="gemini-2.5-flash-preview-04-17", # Changed model name to specific preview version
        generation_config={"response_mime_type": "application/json"} # Request JSON output
    )

    # Prepare the prompt for Gemini
    # We send all sentences in one go, asking for a JSON array of feedback objects.
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
  "feedback": null, // Note: the value is null (the JSON null literal), not the string "null"
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
                        "raw_response": response_text,
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


@app.route('/sentence_practice', methods=['GET', 'POST'])
def sentence_practice():
    """Handle the sentence practice page for errors."""
    # Check if session exists
    if 'errors' not in session or not session['errors']:
        return redirect(url_for('index', message="No errors to practice."))
    
    if request.method == 'POST':
        user_submitted_sentences_text = []
        for i in range(len(session['errors'])):
            sentence_text = request.form.get(f'sentence_{i}', '').strip()
            user_submitted_sentences_text.append(sentence_text)

        # Get feedback from Gemini for all sentences, including debug info
        gemini_response_data = get_feedback_from_gemini(user_submitted_sentences_text)
        gemini_feedback_results = gemini_response_data["feedback_list"]
        debug_info = gemini_response_data["debug_info"]


        processed_sentences_for_template = []
        timestamp = datetime.now().isoformat()
        
        for i, error_info in enumerate(session['errors']):
            original_sentence_text = user_submitted_sentences_text[i]
            correct_form = error_info['correct']
            
            # Basic check (can be enhanced or replaced by Gemini's feedback)
            contains_correct = correct_form.lower() in original_sentence_text.lower()
            
            # Find the corresponding Gemini feedback
            # Assuming gemini_feedback_results is in the same order
            current_gemini_feedback = gemini_feedback_results[i].get("gemini_feedback", {"error": "Feedback not found"})

            processed_sentences_for_template.append({
                'verb': error_info['verb'],
                'tense': error_info['tense'],
                'pronoun': error_info['pronoun'],
                'correct_form': correct_form,
                'sentence': original_sentence_text, # The user's submitted sentence
                'is_correct': contains_correct, # Original basic check
                'timestamp': timestamp,
                'gemini_feedback': current_gemini_feedback # Add Gemini's feedback here
            })
        
        # Save sentences (original user sentences, not Gemini feedback directly into sentences.json,
        # but the processed_sentences_for_template will be used for display)
        # We might want to decide if/how Gemini feedback is persisted.
        # For now, let's save the user's attempt as before.
        sentences_to_save = []
        for s_data in processed_sentences_for_template:
            sentences_to_save.append({
                'verb': s_data['verb'],
                'tense': s_data['tense'],
                'pronoun': s_data['pronoun'],
                'correct_form': s_data['correct_form'],
                'sentence': s_data['sentence'],
                'is_correct': s_data['is_correct'], # The basic check
                'timestamp': s_data['timestamp']
                # Not saving gemini_feedback to sentences.json by default
            })

        all_sentences = load_sentences()
        all_sentences.extend(sentences_to_save)
        save_sentences(all_sentences)
        
        # Clear session
        session.pop('exercises', None)
        session.pop('current_index', None)
        session.pop('errors', None)
        
        # Pass debug_info to the template
        return render_template('sentence_results.html', sentences=processed_sentences_for_template)
    
    # GET request
    # Pass TENSE_NAMES to the template for use in prompts and displaying tense names correctly
    return render_template('sentence_practice.html', errors=session['errors'], tense_names=TENSE_NAMES)

@app.route('/clear_session_and_index')
def clear_session_and_index():
    """Clear session variables and redirect to index."""
    session.pop('exercises', None)
    session.pop('current_index', None)
    session.pop('errors', None)
    return redirect(url_for('index', message="Congratulations! All exercises completed correctly."))

@app.route('/records')
def records():
    """Show records of all verb conjugations."""
    results = load_results()
    preferences = load_preferences()
    
    # Organize data for display
    verbs_data = {}
    for verb in VERBS:
        verbs_data[verb] = {}
        for tense in VERBS[verb]:
            verb_tense_key = f"{verb}_{tense}"
            
            # Get results for this verb and tense
            tense_results = results.get(verb_tense_key, {})
            
            # Check if all conjugations are correct
            all_correct = all(tense_results.get(pronoun, {}).get("correct", False) 
                             for pronoun in PRONOUNS)
            
            # Get preferences
            prefs = preferences.get(verb, {}).get(tense, {})
            never_show = prefs.get("never_show", False)
            always_show = prefs.get("always_show", False)
            
            verbs_data[verb][tense] = {
                "results": tense_results,
                "all_correct": all_correct,
                "never_show": never_show,
                "always_show": always_show
            }
    
    return render_template('records.html', 
                          verbs_data=verbs_data, 
                          verbs=VERBS, 
                          tense_names=TENSE_NAMES,
                          pronouns=PRONOUNS)

@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    """Update verb preferences."""
    preferences = load_preferences()
    verb = request.form.get('verb')
    tense = request.form.get('tense')
    never_show = request.form.get('never_show') == 'true'
    always_show = request.form.get('always_show') == 'true'
    
    if verb in preferences and tense in preferences[verb]:
        preferences[verb][tense]["never_show"] = never_show
        preferences[verb][tense]["always_show"] = always_show
    
    save_preferences(preferences)
    return jsonify({"success": True})

@app.route('/sentences')
def sentences():
    """Show all recorded sentences."""
    all_sentences = load_sentences()
    return render_template('sentences.html', sentences=all_sentences, tense_names=TENSE_NAMES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=53210, debug=True)
