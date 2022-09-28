from flask import Flask


def create_app():
    # Create a Flask app object and pass it this package
    app = Flask(__name__)

    # Set the default configuration settings as defined in config.py
    app.config.from_object("config.app_config")

    @app.get('/')
    def index():
        return {"message": "Welcome to the AskLocal web server API!"}

    return app
