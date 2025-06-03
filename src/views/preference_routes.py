from flask import Blueprint, jsonify, request
from ..data_access import file_handler # Import file_handler

bp = Blueprint('preference', __name__)

@bp.route('/update_preferences', methods=['POST'])
def update_preferences():
    """Update verb preferences."""
    preferences = file_handler.load_preferences()
    verb = request.form.get('verb')
    tense = request.form.get('tense')
    never_show = request.form.get('never_show') == 'true'
    always_show = request.form.get('always_show') == 'true'
    show_primarily = request.form.get('show_primarily') == 'true'  # New preference

    if verb not in preferences:
        preferences[verb] = {}
    if tense not in preferences[verb]:
        # Initialize with defaults, including the new show_primarily
        preferences[verb][tense] = {"never_show": False, "always_show": False, "show_primarily": False}

    preferences[verb][tense]["never_show"] = never_show
    preferences[verb][tense]["always_show"] = always_show
    preferences[verb][tense]["show_primarily"] = show_primarily  # Save the new preference

    file_handler.save_preferences(preferences)
    return jsonify({"success": True})
