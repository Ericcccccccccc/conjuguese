import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder='../templates', static_folder='../static')
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this in production
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    from .views import main_routes, exercise_routes, preference_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(exercise_routes.bp)
    app.register_blueprint(preference_routes.bp)

    # Add Jinja globals
    app.jinja_env.globals['enumerate'] = enumerate

    return app

app = create_app()
