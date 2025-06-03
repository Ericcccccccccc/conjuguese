import random
from datetime import datetime
from ..data_access import file_handler # Import file_handler for now
from ..core_data import VERBS, PRONOUNS
from . import gemini_service # Import gemini_service

def get_available_exercises():
    """Get lists of available exercises (primary and secondary) based on preferences and results."""
    results = file_handler.load_results()
    preferences = file_handler.load_preferences()
    primary_pool = []
    secondary_pool = []

    for verb in VERBS:
        for tense in VERBS[verb]:
            verb_prefs = preferences.get(verb, {}).get(tense, {})
            never_show = verb_prefs.get("never_show", False)
            always_show = verb_prefs.get("always_show", False)
            show_primarily = verb_prefs.get("show_primarily", False)

            if never_show:
                continue

            verb_tense_key = f"{verb}_{tense}"
            all_correct = False
            if verb_tense_key in results:
                all_correct = all(results[verb_tense_key].get(pronoun, {}).get("correct", False)
                                 for pronoun in PRONOUNS)

            exercise_tuple = (verb, tense)

            if show_primarily:
                if not all_correct or always_show:
                    primary_pool.append(exercise_tuple)
                # If it's show_primarily but completed and not always_show, it could still be in secondary
                elif all_correct and not always_show: 
                    pass # Don't add to primary, will be handled by secondary logic if needed
                else: # Not completed, add to primary (this case should be covered by 'not all_correct')
                    primary_pool.append(exercise_tuple)

            # Add to secondary pool if not show_primarily and meets criteria,
            # OR if it was show_primarily but completed and not always_show (so it wasn't added to primary)
            # This ensures items marked show_primarily but completed (and not always_show) are not lost
            # and can be picked if the primary pool is exhausted.
            if not show_primarily:
                 if not all_correct or always_show:
                    secondary_pool.append(exercise_tuple)
            elif all_correct and not always_show: # Was show_primarily, completed, not always_show
                secondary_pool.append(exercise_tuple)


    random.shuffle(primary_pool)
    random.shuffle(secondary_pool)
    return primary_pool, secondary_pool

def select_exercises(count=5):
    """Select a specified number of exercises, aiming for a mix from primary and secondary pools."""
    primary_pool, secondary_pool = get_available_exercises()
    
    selected_exercises = []
    
    # Define target counts for each pool
    primary_target_count = 3
    if count < primary_target_count: # Adjust if total count is less than primary target
        primary_target_count = count
        secondary_target_count = 0
    else:
        secondary_target_count = count - primary_target_count

    # Take from primary pool up to its target
    actual_taken_from_primary = min(primary_target_count, len(primary_pool))
    selected_exercises.extend(primary_pool[:actual_taken_from_primary])
    
    # Keep track of remaining items in pools
    remaining_primary_pool = primary_pool[actual_taken_from_primary:]
    
    # Take from secondary pool up to its target
    if secondary_target_count > 0:
        actual_taken_from_secondary = min(secondary_target_count, len(secondary_pool))
        selected_exercises.extend(secondary_pool[:actual_taken_from_secondary])
        remaining_secondary_pool = secondary_pool[actual_taken_from_secondary:]
    else:
        remaining_secondary_pool = secondary_pool # Or just secondary_pool if no target

    # If not enough exercises selected, try to fill from remaining pools
    current_selected_count = len(selected_exercises)
    if current_selected_count < count:
        needed_more = count - current_selected_count
        
        # Try to fill from remaining primary first
        fill_from_remaining_primary = min(needed_more, len(remaining_primary_pool))
        if fill_from_remaining_primary > 0:
            selected_exercises.extend(remaining_primary_pool[:fill_from_remaining_primary])
            needed_more -= fill_from_remaining_primary
            
        # Then, try to fill from remaining secondary
        if needed_more > 0:
            fill_from_remaining_secondary = min(needed_more, len(remaining_secondary_pool))
            if fill_from_remaining_secondary > 0:
                selected_exercises.extend(remaining_secondary_pool[:fill_from_remaining_secondary])

    # Ensure unique exercises if somehow duplicates were added (though current logic shouldn't cause this)
    # This can be more robust by converting to set of tuples and back to list if order doesn't matter
    # For now, assuming the pool separation and slicing prevents duplicates.
    # random.shuffle(selected_exercises) # Optionally shuffle the final list
            
    return selected_exercises

def update_results(verb, tense, user_answers):
    """Update the results file with the latest exercise results."""
    results = file_handler.load_results()
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

    file_handler.save_results(results)

def process_exercise_submission(verb, tense, user_answers):
    """
    Processes a user's exercise submission, updates results, and returns feedback.
    Returns a dictionary with results_list, all_correct, and errors_list.
    """
    correct_conjugations = VERBS[verb][tense]

    current_results_list = []
    current_all_correct = True
    errors_list = []

    for i, (user, correct) in enumerate(zip(user_answers, correct_conjugations)):
        is_correct = user.strip().lower() == correct.lower() # Case-insensitive comparison
        if not is_correct:
            current_all_correct = False
            errors_list.append({
                'verb': verb,
                'tense': tense,
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
    update_results(verb, tense, user_answers)

    # Return the complete errors_list for the current exercise
    return {
        'results_list': current_results_list,
        'all_correct': current_all_correct,
        'errors_list': errors_list
    }

def get_gemini_sentence_feedback(user_sentence, verb, tense, pronoun, correct_form):
    """
    Gets detailed feedback for a single sentence from Gemini.
    """
    # Call the gemini_service to get feedback for a list containing one sentence
    gemini_response_data = gemini_service.get_feedback_from_gemini([user_sentence])
    
    # Extract the feedback for the single sentence
    feedback_list = gemini_response_data.get("feedback_list", [])
    
    if feedback_list:
        # The first (and only) item in the feedback_list contains the gemini_feedback
        return feedback_list[0].get("gemini_feedback")
    else:
        # Return an error or default structure if no feedback was returned
        return {"error": "No feedback received from Gemini service."}
