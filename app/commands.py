from flask import Blueprint
from app import db

# Import models
from app.models.answer import Answer
from app.models.category import Category
from app.models.country import Country
from app.models.locations import Location
from app.models.postcode import Postcode
from app.models.question import Question
from app.models.recommendation import Recommendation
from app.models.user import User


# Instantiate a blueprint for CLI database commands
db_commands = Blueprint("db", __name__)


@db_commands.cli.command("create")
def create_tables():
    """ Create all tables in the connected database using models """
    db.create_all()
    print("Database: Tables created")


@db_commands.cli.command("drop")
def create_tables():
    """ Drop all tables in the connected database """
    db.drop_all()
    print("Database: Tables dropped")


@db_commands.cli.command("seed")
def create_tables():
    """ Seed all tables in the connected database """

    print("Database: Tables seeded")
