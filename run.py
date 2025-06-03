from src import app

if __name__ == '__main__':
    # Consider moving host/port/debug to config if they vary by environment
    app.run(host='0.0.0.0', port=53210, debug=True)
