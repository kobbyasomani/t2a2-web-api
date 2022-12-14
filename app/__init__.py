from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Instantiate extensions used by the app
db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    """ Create the Flask application object """
    # Create a Flask app object and pass it this package
    app = Flask(__name__)

    # Set the default configuration settings as defined in config.py
    app.config.from_object("config.app_config")

    # Initialise extension instances for use with the app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register CLI commands for database
    from app.commands import db_commands
    app.register_blueprint(db_commands)

    # Import controllers
    from app.controllers import registerable_controllers
    for controller in registerable_controllers:
        app.register_blueprint(controller)

    return app
