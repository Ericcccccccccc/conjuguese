"""
Portuguese Verb Conjugation Practice App
"""

import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from data.verbs import VERBS, TENSE_NAMES, PRONOUNS

app = Flask(__name__)
app.secret_key = 'portuguese_conjugation_app_secret_key'  # Required for session

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
        verb, tense = session['exercises'][session['current_index']]
        correct_conjugations = VERBS[verb][tense]
        
        # Get user answers
        user_answers = [
            request.form.get(f'answer_{i}', '').strip().lower()
            for i in range(4)
        ]
        
        # Check answers
        results = []
        all_correct = True
        for i, (user, correct) in enumerate(zip(user_answers, correct_conjugations)):
            is_correct = user == correct
            if not is_correct:
                all_correct = False
                # Add to errors list for sentence practice later
                if 'errors' not in session:
                    session['errors'] = []
                session['errors'].append({
                    'verb': verb,
                    'tense': tense,
                    'pronoun': PRONOUNS[i],
                    'correct': correct,
                    'user_answer': user
                })
            
            results.append({
                'pronoun': PRONOUNS[i],
                'user_answer': user,
                'correct_answer': correct,
                'is_correct': is_correct
            })
        
        # Update results file
        update_results(verb, tense, user_answers)
        
        # Move to next exercise or finish
        session['current_index'] += 1
        
        if session['current_index'] >= len(session['exercises']):
            # All exercises completed
            if session.get('errors', []):
                return redirect(url_for('sentence_practice'))
            else:
                # Clear session
                session.pop('exercises', None)
                session.pop('current_index', None)
                session.pop('errors', None)
                return redirect(url_for('index', message="Congratulations! All exercises completed correctly."))
        
        return render_template('results.html', 
                              verb=verb, 
                              tense=tense, 
                              tense_name=TENSE_NAMES[tense],
                              results=results,
                              all_correct=all_correct,
                              next_url=url_for('exercise'))
    
    # GET request - show the current exercise
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

@app.route('/sentence_practice', methods=['GET', 'POST'])
def sentence_practice():
    """Handle the sentence practice page for errors."""
    # Check if session exists
    if 'errors' not in session or not session['errors']:
        return redirect(url_for('index', message="No errors to practice."))
    
    if request.method == 'POST':
        sentences = []
        timestamp = datetime.now().isoformat()
        
        for i, error in enumerate(session['errors']):
            sentence = request.form.get(f'sentence_{i}', '').strip()
            correct_form = error['correct']
            
            # Check if the sentence contains the correct conjugation
            contains_correct = correct_form.lower() in sentence.lower()
            
            sentences.append({
                'verb': error['verb'],
                'tense': error['tense'],
                'pronoun': error['pronoun'],
                'correct_form': correct_form,
                'sentence': sentence,
                'is_correct': contains_correct,
                'timestamp': timestamp
            })
        
        # Save sentences
        all_sentences = load_sentences()
        all_sentences.extend(sentences)
        save_sentences(all_sentences)
        
        # Clear session
        session.pop('exercises', None)
        session.pop('current_index', None)
        session.pop('errors', None)
        
        return render_template('sentence_results.html', sentences=sentences)
    
    return render_template('sentence_practice.html', errors=session['errors'])

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