import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() # Load environment variables from .env

# Flask Secret Key (used by __init__.py, but defined here for clarity)
# app.secret_key = 'portuguese_conjugation_app_secret_key' # Moved to __init__.py create_app function

# Gemini API Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"DEBUG: GOOGLE_GEMINI_API_KEY found and configured.")
else:
    print("WARNING: GOOGLE_GEMINI_API_KEY not found in environment variables. Gemini features may be disabled.")

# Data File Paths (for current JSON storage)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data') # Adjust path to point to the data directory at the project root
RESULTS_FILE = os.path.join(DATA_DIR, 'results.json')
SENTENCES_FILE = os.path.join(DATA_DIR, 'sentences.json')
PREFERENCES_FILE = os.path.join(DATA_DIR, 'preferences.json')
# SESSION_FILE = os.path.join(DATA_DIR, 'current_session.json') # This was not used in app.py, can be removed

# Future Database Configuration (Placeholder)
DATABASE_URL = os.getenv('DATABASE_URL') # Example for Supabase connection string
