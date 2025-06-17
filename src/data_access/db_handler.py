from src.config import supabase
from src.core_data import VERBS # For initializing preferences

from src.config import supabase
from src.core_data import VERBS # For initializing preferences

DEFAULT_USER_ID = "single_user" # Placeholder for single-user mode

def load_results(user_id: str = DEFAULT_USER_ID):
    """Load results from the Supabase 'results' table for a given user."""
    if supabase is None:
        print("Supabase client not initialized. Cannot load results.")
        return {}

    try:
        response = supabase.table('results').select('*').eq('user_id', user_id).execute()
        data = response.data
        
        # Transform flat list of results into nested dictionary structure,
        # keeping only the latest result for each verb-tense-pronoun combination.
        # {verb_tense_key: {pronoun: {result_data}}}
        
        # Sort data by timestamp to easily pick the latest
        data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        results_dict = {}
        processed_combinations = set() # To keep track of (verb_tense_key, pronoun) already processed

        for item in data:
            verb = item.get('verb')
            tense = item.get('tense')
            pronoun = item.get('pronoun')
            
            if verb and tense and pronoun:
                verb_tense_key = f"{verb}_{tense}"
                combination_key = (verb_tense_key, pronoun)

                # Only process if this combination hasn't been processed yet (meaning we found the latest)
                if combination_key not in processed_combinations:
                    if verb_tense_key not in results_dict:
                        results_dict[verb_tense_key] = {}
                    
                    # Store relevant fields for the latest result
                    results_dict[verb_tense_key][pronoun] = {
                        "user_answer": item.get("user_answer"),
                        "timestamp": item.get("timestamp"),
                        "correct": item.get("is_correct")
                    }
                    processed_combinations.add(combination_key)
        return results_dict
    except Exception as e:
        print(f"Error loading results from Supabase: {e}")
        return {}

def save_result(result_data: dict, user_id: str = DEFAULT_USER_ID):
    """Save a single exercise result to the Supabase 'results' table."""
    if supabase is None:
        print("Supabase client not initialized. Cannot save result.")
        return

    try:
        # Ensure user_id is set in the data being saved
        result_data['user_id'] = user_id
            
        response = supabase.table('results').insert([result_data]).execute()
        if response.data:
            print(f"Result saved: {response.data}")
        else:
            print(f"Failed to save result: {response.error}")
    except Exception as e:
        print(f"Error saving result to Supabase: {e}")

def load_sentences(user_id: str = DEFAULT_USER_ID):
    """Load recorded sentences from the Supabase 'sentences' table for a given user."""
    if supabase is None:
        print("Supabase client not initialized. Cannot load sentences.")
        return []

    try:
        response = supabase.table('sentences').select('*').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error loading sentences from Supabase: {e}")
        return []

def save_sentence(sentence_data: dict, user_id: str = DEFAULT_USER_ID):
    """Save a single recorded sentence to the Supabase 'sentences' table."""
    if supabase is None:
        print("Supabase client not initialized. Cannot save sentence.")
        return

    try:
        # Ensure user_id is set in the data being saved
        sentence_data['user_id'] = user_id
            
        response = supabase.table('sentences').insert([sentence_data]).execute()
        if response.data:
            print(f"Sentence saved: {response.data}")
        else:
            print(f"Failed to save sentence: {response.error}")
    except Exception as e:
        print(f"Error saving sentence to Supabase: {e}")

def load_preferences(user_id: str = DEFAULT_USER_ID):
    """Load preferences from the Supabase 'preferences' table for a given user."""
    if supabase is None:
        print("Supabase client not initialized. Cannot load preferences.")
        # If Supabase is not initialized, return default preferences
        return {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                             for tense in VERBS[verb]}
                      for verb in VERBS}

    try:
        response = supabase.table('preferences').select('*').eq('user_id', user_id).execute()
        data = response.data
        
        # Transform flat list of preferences into nested dictionary structure
        # {verb: {tense: {never_show: bool, always_show: bool, show_primarily: bool}}}
        preferences_dict = {}
        for item in data:
            verb = item.get('verb')
            tense = item.get('tense')
            
            if verb and tense:
                if verb not in preferences_dict:
                    preferences_dict[verb] = {}
                preferences_dict[verb][tense] = {
                    "never_show": item.get("never_show", False),
                    "always_show": item.get("always_show", False),
                    "show_primarily": item.get("show_primarily", False)
                }
        
        # Merge with default preferences to ensure all verbs/tenses are present
        default_preferences = {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                                     for tense in VERBS[verb]}
                              for verb in VERBS}
        
        # Deep merge: existing preferences override defaults
        for verb, tenses in default_preferences.items():
            if verb not in preferences_dict:
                preferences_dict[verb] = {}
            for tense, default_prefs in tenses.items():
                if tense not in preferences_dict[verb]:
                    preferences_dict[verb][tense] = default_prefs
                else:
                    # Merge individual preference flags
                    for key, value in default_prefs.items():
                        if key not in preferences_dict[verb][tense]:
                            preferences_dict[verb][tense][key] = value

        return preferences_dict
    except Exception as e:
        print(f"Error loading preferences from Supabase: {e}")
        # Fallback to default preferences if there's an error
        preferences = {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                             for tense in VERBS[verb]}
                      for verb in VERBS}
        return preferences

def save_preference(preference_data: dict, user_id: str = DEFAULT_USER_ID):
    """Save a single preference entry to the Supabase 'preferences' table using upsert."""
    if supabase is None:
        print("Supabase client not initialized. Cannot save preference.")
        return

    try:
        # Ensure user_id is set in the data being saved
        preference_data['user_id'] = user_id
            
        response = supabase.table('preferences').upsert(preference_data, on_conflict='user_id,verb,tense').execute()
        if response.data:
            print(f"Preference saved/updated: {response.data}")
        else:
            print(f"Failed to save/update preference: {response.error}")
    except Exception as e:
        print(f"Error saving preference to Supabase: {e}")
