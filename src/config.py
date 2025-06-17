import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

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

# Supabase Configuration
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("DEBUG: Supabase client initialized.")
else:
    print("WARNING: Supabase URL or Key not found in environment variables. Database features may be disabled.")
