from flask import Blueprint
from app import db, bcrypt
from datetime import datetime, timezone, timedelta
import csv

# Import models
from app.models.answer import Answer
from app.models.category import Category
from app.models.country import Country
from app.models.location import Location
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

    # Seed countries from txt file
    with open("./app/data/countryInfo.txt", "r") as country_info:
        countries_reader = csv.reader(country_info, delimiter="\t")
        for country in countries_reader:
            new_country = Country(
                country_code=country[0],
                country=country[4]
            )
            db.session.add(new_country)
            db.session.commit()
    country_info.close()

    # Seed Australian locations from txt file
    with open("./app/data/AU.txt") as locations_AU:
        locations_reader = csv.reader(locations_AU, delimiter="\t")
        for location in locations_reader:
            new_location = Location(
                country_code=location[0],
                state=location[3],
                postcode=location[1],
                suburb=location[2]
            )
            db.session.add(new_location)
            db.session.commit()
    locations_AU.close()

    # Add question categories
    categories = {
        "Accommodation": "hotels and short-term rentals",
        "Housing": "renting or buying properties",
        "Venues": "cultural, entertainment, and sports venues",
        "Food & Drink": "grocery stores, restaurants, cafés, and bars",
        "Shopping": "retail stores and shopping centres",
        "Transport": "public transport, taxis, and ride-sharing",
        "Money": "ATMs, banks, insurance, and financial services",
        "Health & Medicine": (
            "pharmacies, doctors, "
            "health practitioners, and hospitals"),
        "Services": "post, vehicle, laundromat, and other services",
        "Trades": "plumbing, electrical, carpentry, and other trade services",
        "Miscellaneous": "miscellaneous topics"
    }

    for cat_name, cat_description in categories.items():
        category = Category(
            category_name=cat_name,
            description=f"Questions about {cat_description}"
        )
        db.session.add(category)

    # Add users
    user1 = User(
        username="user1",
        email="user1@emailprovider.com",
        password=bcrypt.generate_password_hash("12345678").decode("utf-8")
    )
    db.session.add(user1)

    user2 = User(
        username="user2",
        email="user2@emailprovider.com",
        password=bcrypt.generate_password_hash("12345678").decode("utf-8")
    )
    db.session.add(user2)
    db.session.commit()

    # Add a question
    question1 = Question(
        user_id=1,
        location_id=14982,
        category_id=1,
        date_time=datetime.now(timezone.utc),
        body=(
            "Hello! I'm moving to Perth soon.\nWhat's a good low-cost place "
            "to stay for a few nights after arriving?")
    )
    db.session.add(question1)

    # Add a second question
    question2 = Question(
        user_id=1,
        location_id=185,
        category_id=4,
        date_time=datetime.now(timezone.utc),
        body=("I'm looking for a good coffee shop in my area.")
    )
    db.session.add(question2)

    # Add a third question
    question3 = Question(
        user_id=2,
        location_id=572,
        category_id=7,
        date_time=datetime.now(timezone.utc),
        body=("What's the closest 24-hour ATMs in this neighbourhood?")
    )
    db.session.add(question3)

    # Add an answer
    answer1 = Answer(
        user_id=2,
        question_id=1,
        parent_id=None,
        date_time=datetime.now(timezone.utc) + timedelta(hours=1),
        body=(
            "Welcome!\nAre you looking for a hostel or a hotel, "
            "and how many people do you need to fit?")
    )
    db.session.add(answer1)

    # Add a reply to an answer (answer with parent)
    reply1 = Answer(
        user_id=1,
        question_id=1,
        parent_id=1,
        date_time=datetime.now(timezone.utc) + timedelta(hours=2),
        body=("I'm a solo traveller and looking for a hotel.")
    )
    db.session.add(reply1)

    # Add a nested reply (a reply to a reply)
    reply2 = Answer(
        user_id=2,
        question_id=1,
        parent_id=2,
        date_time=datetime.now(timezone.utc) + timedelta(hours=2.5),
        body=(
            "ibis Perth is pretty close to the city centre and not "
            "too expensive.")
    )
    db.session.add(reply2)

    # Add a recommendation
    recommendation1 = Recommendation(
        user_id=1,
        answer_id=1
    )
    db.session.add(recommendation1)

    db.session.commit()
    print("Database: Tables seeded")
