from flask import Blueprint, jsonify, request
from ..data_access import db_handler

bp = Blueprint('preference', __name__)

@bp.route('/update_preferences', methods=['POST'])
def update_preferences():
    """Update verb preferences."""
    preferences = db_handler.load_preferences(db_handler.DEFAULT_USER_ID)
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

    preference_data = {
        "verb": verb,
        "tense": tense,
        "never_show": never_show,
        "always_show": always_show,
        "show_primarily": show_primarily
    }
    db_handler.save_preference(preference_data, db_handler.DEFAULT_USER_ID)
    return jsonify({"success": True})
