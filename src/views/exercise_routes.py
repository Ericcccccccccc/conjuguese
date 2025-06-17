from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
import json
import random
from ..services import exercise_service
from ..core_data import TENSE_NAMES, PRONOUNS, VERBS
from ..data_access import db_handler # Import db_handler

bp = Blueprint('exercise', __name__)

@bp.route('/start_exercises')
def start_exercises():
    """Start a new set of exercises."""
    exercises = exercise_service.select_exercises(5)
    if not exercises:
        return redirect(url_for('main.index', message="No exercises available. Please adjust your preferences."))

    session['exercises'] = exercises
    session['current_index'] = 0
    session['all_errors_in_session'] = []
    session['sentence_errors'] = []
    session['remediation_errors'] = []
    session['remediation_results'] = []
    session['sentence_practice_results'] = []

    return redirect(url_for('exercise.exercise'))

@bp.route('/exercise', methods=['GET', 'POST'])
def exercise():
    """Handle the exercise page."""
    if 'exercises' not in session or not session['exercises']:
        return redirect(url_for('main.index', message="Session expired or no exercises found."))

    if request.method == 'POST':
        current_verb, current_tense = session['exercises'][session['current_index']]
        user_answers = [request.form.get(f'answer_{i}', '').strip() for i in range(len(PRONOUNS))]

        processing_results = exercise_service.process_exercise_submission(
            current_verb, current_tense, user_answers, db_handler.DEFAULT_USER_ID
        )
        current_exercise_errors = processing_results.get('errors_list', [])
        session['all_errors_in_session'].extend(current_exercise_errors)
        session['current_index'] += 1

        next_url_for_results_page = ''
        button_text_for_results_page = ''

        if session['current_index'] >= len(session['exercises']):
            all_errors = session.pop('all_errors_in_session', [])
            # Removed random.shuffle(all_errors) for deterministic behavior, especially for testing.
            # If random order is desired for UX, it should be applied consistently elsewhere or re-added with a seed for tests.

            if len(all_errors) > 5:
                session['sentence_errors'] = all_errors[:5]
                session['remediation_errors'] = all_errors[5:]
            else:
                session['sentence_errors'] = all_errors
                session['remediation_errors'] = []

            if session.get('sentence_errors', []) or session.get('remediation_errors', []):
                next_url_for_results_page = url_for('exercise.remediation_flow')
                button_text_for_results_page = "Continuar Remediação"
            else:
                next_url_for_results_page = url_for('main.clear_session_and_index', status='success_initial')
                button_text_for_results_page = "Finalizar Exercício"
        else:
            next_url_for_results_page = url_for('exercise.exercise')
            button_text_for_results_page = "Próximo Exercício"

        session['current_exercise_results'] = {
            'verb': current_verb,
            'tense': current_tense,
            'tense_name': TENSE_NAMES[current_tense],
            'results': processing_results['results_list'],
            'all_correct': processing_results['all_correct'],
            'next_url': next_url_for_results_page,
            'button_text': button_text_for_results_page
        }
        return redirect(url_for('exercise.show_exercise_results'))

    else: # GET request - show the current exercise
        if session['current_index'] >= len(session['exercises']):
            if session.get('sentence_errors', []) or session.get('remediation_errors', []):
                return redirect(url_for('exercise.remediation_flow'))
            else:
                return redirect(url_for('main.clear_session_and_index'))

        verb, tense = session['exercises'][session['current_index']]
        correct_conjugations = VERBS[verb][tense]
        print(f"DEBUG: correct_conjugations: {correct_conjugations}")
        print(f"DEBUG: correct_conjugations tojson: {json.dumps(correct_conjugations)}")
        return render_template('exercise.html',
                              verb=verb,
                              tense=tense,
                              tense_name=TENSE_NAMES[tense],
                              pronouns=PRONOUNS,
                              exercise_num=session['current_index'] + 1,
                              total_exercises=len(session['exercises']),
                              correct_conjugations=correct_conjugations)

@bp.route('/exercise_results')
def show_exercise_results():
    """Display the results of the last exercise submission."""
    if 'current_exercise_results' not in session:
        return redirect(url_for('main.index', message="No exercise results found."))

    results_data = session.pop('current_exercise_results')
    return render_template('results.html', **results_data)

@bp.route('/remediation_flow', methods=['GET', 'POST'])
def remediation_flow():
    """Handle the remediation practice and results flow."""
    if 'remediation_errors' not in session and 'sentence_errors' not in session and 'remediation_results' not in session and 'sentence_practice_results' not in session:
        return redirect(url_for('main.index', message="No errors to remediate or practice sentences."))

    if request.method == 'POST':
        user_word_answers = {}
        for key, value in request.form.items():
            if key.startswith('remediation_word_'):
                index = int(key.split('_')[2])
                user_word_answers[index] = value.strip().lower()

        remediation_results = []
        remaining_remediation_errors = []

        for i, error in enumerate(session.get('remediation_errors', [])):
            user_answer = user_word_answers.get(i, '').strip().lower()
            correct_answer = error['correct'].lower()
            is_correct = user_answer == correct_answer

            remediation_results.append({
                'error': error,
                'user_answer': user_answer,
                'is_correct': is_correct
            })

            if not is_correct:
                remaining_remediation_errors.append(error)
        
        user_sentence_answers = {}
        for key, value in request.form.items():
            if key.startswith('remediation_sentence_'):
                index = int(key.split('_')[2])
                user_sentence_answers[index] = value.strip()

        sentence_practice_results = []
        remaining_sentence_errors = []

        for i, error in enumerate(session.get('sentence_errors', [])):
            user_sentence = user_sentence_answers.get(i, '').strip()
            
            is_sentence_correct = False
            user_words = [word.strip().lower() for word in user_sentence.split()]
            correct_form_lower = error['correct'].lower()

            if correct_form_lower in user_words:
                is_sentence_correct = True

            sentence_practice_results.append({
                'verb': error['verb'],
                'tense': error['tense'],
                'pronoun': error['pronoun'],
                'correct_form': error['correct'],
                'sentence': user_sentence,
                'is_correct': is_sentence_correct,
                'index': i
            })

            if not is_sentence_correct:
                remaining_sentence_errors.append(error)

        # Save each practiced sentence to the database
        from ..data_access import db_handler # Import here to avoid circular dependency if needed, or at top
        for sentence_data_with_index in sentence_practice_results:
            # Create a copy and remove the 'index' key as it's not part of the database schema
            sentence_data_for_db = {k: v for k, v in sentence_data_with_index.items() if k != 'index'}
            db_handler.save_sentence(sentence_data_for_db, db_handler.DEFAULT_USER_ID)

        session['remediation_errors'] = remaining_remediation_errors
        session['remediation_results'] = remediation_results
        session['sentence_errors'] = remaining_sentence_errors
        session['sentence_practice_results'] = sentence_practice_results
        is_remediation_successful = not (remaining_remediation_errors or remaining_sentence_errors)
        session['is_remediation_successful'] = is_remediation_successful

        return redirect(url_for('exercise.remediation_flow'))

    else: # GET request - display remediation practice or results
        current_remediation_results = session.pop('remediation_results', [])
        current_sentence_practice_results = session.pop('sentence_practice_results', [])
        is_remediation_successful = session.pop('is_remediation_successful', None)

        remediation_errors = session.get('remediation_errors', [])
        sentence_errors = session.get('sentence_errors', [])

        if current_remediation_results or current_sentence_practice_results:
            print(f"DEBUG: current_sentence_practice_results before rendering: {current_sentence_practice_results}")
            return render_template('remediation_results.html',
                                   TENSE_NAMES=TENSE_NAMES,
                                   remediation_results=current_remediation_results,
                                   sentence_practice_results=current_sentence_practice_results,
                                   is_remediation_successful=is_remediation_successful)
        elif remediation_errors or sentence_errors:
            return render_template('remediation_practice.html',
                                   TENSE_NAMES=TENSE_NAMES,
                                   remediation_errors=remediation_errors,
                                   sentence_errors=sentence_errors)
        else:
            status_to_pass = 'success_remediation' if not (remediation_errors or sentence_errors) else 'failed_remediation'
            return redirect(url_for('main.clear_session_and_index', status=status_to_pass))

@bp.route('/get_sentence_feedback', methods=['POST'])
def get_sentence_feedback():
    """API endpoint to get Gemini feedback for a single sentence."""
    data = request.get_json()
    user_sentence = data.get('user_sentence')
    verb = data.get('verb')
    tense = data.get('tense')
    pronoun = data.get('pronoun')
    correct_form = data.get('correct_form')

    if not all([user_sentence, verb, tense, pronoun, correct_form]):
        return jsonify({"error": "Missing data for feedback request."}), 400

    gemini_feedback = exercise_service.get_gemini_sentence_feedback(
        user_sentence, verb, tense, pronoun, correct_form
    )
    return jsonify(gemini_feedback)
