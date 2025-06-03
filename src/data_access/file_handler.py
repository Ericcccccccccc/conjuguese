import json
import os
from ..config import RESULTS_FILE, SENTENCES_FILE, PREFERENCES_FILE
from ..core_data import VERBS # Import VERBS for ensure_data_files

def ensure_data_files():
    """Ensure all data files exist with proper structure."""
    # Ensure data directory exists (already handled by config, but good to be safe)
    data_dir = os.path.dirname(RESULTS_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

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

def load_results():
    """Load results from the results file."""
    try:
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} # Return empty dict if file not found or is invalid JSON

def save_results(results):
    """Save results to the results file."""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4) # Add indent for readability

def load_sentences():
    """Load sentences from the sentences file."""
    try:
        with open(SENTENCES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # Return empty list if file not found or is invalid JSON

def save_sentences(sentences):
    """Save sentences to the sentences file."""
    with open(SENTENCES_FILE, 'w') as f:
        json.dump(sentences, f, indent=4) # Add indent for readability

def load_preferences():
    """Load preferences from the preferences file."""
    try:
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If preferences file is missing or invalid, regenerate based on current VERBS
        preferences = {verb: {tense: {"never_show": False, "always_show": False}
                             for tense in VERBS[verb]}
                      for verb in VERBS}
        save_preferences(preferences) # Save the newly generated preferences
        return preferences

def save_preferences(preferences):
    """Save preferences to the preferences file."""
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f, indent=4) # Add indent for readability

# Ensure data files exist on startup
ensure_data_files()
