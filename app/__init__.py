from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instantiate extensions used by the app
db = SQLAlchemy()

def create_app():
    """ Create the Flask application object """
    # Create a Flask app object and pass it this package
    app = Flask(__name__)

    # Set the default configuration settings as defined in config.py
    app.config.from_object("config.app_config")

    # Initialise extension instances for use with the app
    db.init_app(app)

    @app.get('/')
    def index():
        return {"message": "Welcome to the AskLocal web server API!"}

    return app
