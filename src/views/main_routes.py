from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from ..data_access import file_handler # Import file_handler for now
from ..core_data import VERBS, TENSE_NAMES, PRONOUNS

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the main page."""
    # Pass message from redirect if it exists
    message = request.args.get('message')
    return render_template('index.html', message=message)

@bp.route('/clear_session_and_index')
def clear_session_and_index():
    """Clear session variables and redirect to index with a status message."""
    session.pop('exercises', None)
    session.pop('current_index', None)
    session.pop('all_errors_in_session', None) # Clear this too
    session.pop('sentence_errors', None)
    session.pop('remediation_errors', None)
    session.pop('remediation_results', None)
    session.pop('sentence_practice_results', None)
    session.pop('is_remediation_successful', None) # Clear the flag

    status = request.args.get('status')
    message = None

    if status == 'success_initial':
        message = "Parabéns! Todas as conjugações iniciais foram corretas."
    elif status == 'success_remediation':
        message = "Parabéns! Todas as remediações foram concluídas com sucesso."
    elif status == 'failed_remediation':
        message = "Remediação concluída. Continue praticando para melhorar!"
    else:
        message = "Sessão finalizada." # Default message if no specific status

    return redirect(url_for('main.index', message=message)) # Use blueprint name

@bp.route('/records')
def records():
    """Show records of all verb conjugations."""
    results = file_handler.load_results()
    preferences = file_handler.load_preferences()

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

@bp.route('/sentences')
def sentences():
    """Show all recorded sentences."""
    all_sentences = file_handler.load_sentences()
    return render_template('sentences.html', sentences=all_sentences, tense_names=TENSE_NAMES)
