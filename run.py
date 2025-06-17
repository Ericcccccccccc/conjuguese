from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

from src import app

if __name__ == '__main__':
    # Consider moving host/port/debug to config if they vary by environment
    app.run(host='0.0.0.0', port=5000, debug=True)
