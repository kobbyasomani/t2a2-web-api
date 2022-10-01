import os


class Config(object):
    """ Application configuration settings """
    # Turn off SQLALchemy model modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """ Get database URI from .env to use in db connection string """
        URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        # Raise an error if value is empty
        if not URI:
            raise ValueError("The SQLAlchemy database URI has not been set.")

        return URI

    # Get the JWT secret key for signing access tokens
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


# Different configurations using class inheritance
class TestingConfig(Config):
    """ Testing Configuration """
    TESTING = True


class DevelopmentConfig(Config):
    """ Development Configuration """
    DEBUG = True


class ProductionConfig(Config):
    """ Production Configuration """
    pass


# Set the configuration depending on the environment
if os.environ.get("FLASK_DEBUG") == True:
    app_config = DevelopmentConfig()

elif os.environ.get("FLASK_TESTING") == True:
    app_config = TestingConfig()

else:
    app_config = ProductionConfig()
