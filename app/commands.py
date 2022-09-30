from flask import Blueprint
from app import db

# Import models
from app.models.answer import Answer
from app.models.category import Category
from app.models.country import Country
from app.models.location import Location
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
def seed_tables():
    """ Seed all tables in the connected database """

    # Add question categories
    categories = {
        "Accommodation": "hotels and short-term rentals",
        "Housing": "renting or buying properties",
        "Venues": "cultural, entertainment, and sports venues",
        "Food & Drink": "grocery stores, restaurants, cafés, and bars",
        "Shopping": "retail stores and shopping centres",
        "Transport": "public transport, taxis, and ride-sharing",
        "Money": "ATMs, banks, insurance, and financial services",
        "Health & Medicine": ("pharmacies, doctors, "
                                "health practictioners, and hospitals"),
        "Services": "post, vehicle, laundromat, and other services",
        "Trades": "plumbing, electrical, carpentry, and other trade services",
        "Miscellaneous": "miscellaneous topics"
    }

    for cat_name, cat_description in categories.items():
        category = Category(
            name = cat_name,
            description = cat_description
        )
        db.session.add(category)

    # Create a user
    user1 = User(
        # user_id is a sequentially generated integer
        username="user1",
        password="12345678"
    )

    db.session.add(user1)

    db.session.commit()
    print("Database: Tables seeded")
