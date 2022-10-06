from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.utils import duplicate_exists, current_datetime
from app import db
from app.models.question import Question
from app.models.country import Country
from app.models.location import Location
from app.models.category import Category
from app.models.user import User
from app.models.answer import Answer
from app.schemas.question_schema import (
    question_schema, question_details_schema,
    question_update_schema, questions_schema, question_post_schema)
from app.schemas.answer_schema import answer_schema
from app.controllers.users_controller import find_user, get_logged_in_user


questions = Blueprint("questions", __name__, url_prefix="/questions")


def show_questions_list(questions_list):
    if questions_list:
        return jsonify(questions_schema.dump(questions_list))
    else:
        return {"message": "No matching questions were found."}, 404


def location_not_found():
    return {"error": "The location could not be found."}, 404


@questions.get("/")
def get_questions():
    """ Return a list of all questions matching filters """
    filterable_attributes = [
        "user_id",
        "username",
        "category_id",
        "category_name",
        "location_id",
        "country_code",
        "country",
        "state",
        "postcode",
        "suburb",
    ]

    # Check for a query string to filter results
    if request.query_string:
        filter_list = request.args.to_dict()
        join_filters = {
            "question": {},
            "user": {},
            "category": {},
            "location": {},
            "country": {}
        }

        # Check if supplied filter attributes can be used
        valid_filters = True
        for key, value in filter_list.items():
            if key not in filterable_attributes:
                valid_filters = False
            # Convert inputs to match database keys
            if key in ["category_name", "country", "state", "suburb"]:
                filter_list[key] = value.title()

        # Add the filter to relevant join filter list
        for key, value in filter_list.items():
            if key in ["country_code", "state", "postcode", "suburb"]:
                join_filters["location"][key] = filter_list[key]
            elif key in ["country"]:
                join_filters["country"][key] = filter_list[key]
            elif key in ["username"]:
                join_filters["user"][key] = filter_list[key]
            elif key in ["category_name"]:
                join_filters["category"][key] = filter_list[key]
            else:
                join_filters["question"][key] = filter_list[key]

        # Filter questions list using request arguments
        if valid_filters:
            questions_list = Question.query.filter_by(
                **join_filters["question"]).join(
                User.query.filter_by(**join_filters["user"])).join(
                    Location.query.filter_by(
                        **join_filters["location"])).join(
                    Category.query.filter_by(
                        **join_filters["category"])).join(
                            Location.country
            ).all()

            # Query ran successfully
            return show_questions_list(questions_list)

        # One or more filters passed as URL query arguments were invalid
        else:
            return {"error": "You can only filter Questions using "
                    "the following attributes in your query string: "
                    f"{filterable_attributes}. Filters using the _id "
                    "suffix format must be integers. country_code must "
                    "be supplied in two-letter ISO format (e.g., AU "
                    "for Australia)."}, 400
    else:
        questions_list = Question.query.all()
        return show_questions_list(questions_list)


@questions.get("/<int:id>")
def get_question(id):
    """ Return a specific question by id with all of its answers """
    try:
        question = Question.query.get(id)
    except 404:
        return {"error": "The question id must be an integer."}, 404
    if question:
        return jsonify(question_details_schema.dump(question))
    else:
        return {"error": "A question with that id was not found."}, 404


@questions.get("/categories/<id>")
def get_questions_by_category(id):
    """ Return all questions for a given category name or id """
    # Query by category_id
    if id.isdigit():
        questions_list = Question.query.filter(
            Question.category_id == id,
        ).all()

    # Query by category_name
    else:
        questions_list = Question.query.join(
            Question.category).filter_by(
                category_name=id.title()
        ).all()

    return show_questions_list(questions_list)


@questions.post("/")
@jwt_required()
def post_question():
    """ Post a new question """
    # Get the question post fields
    question_fields = question_post_schema.load(request.json, partial=True)

    # Make sure the post has a location
    # Check for either a location_id or fields for a new location
    if ("location_id" not in question_fields.keys() and not all(
            field in question_fields.keys()
            for field in ["country_code", "state", "postcode", "suburb"])
        ):
        return {"error": "You must provide a location_id (integer) "
                "OR a country_code (ISO 3166-1, alpha-2 format), "
                "and the state, postcode, and suburb names as strings."}, 400

    # If location_id is provided, don't accept other location fields
    if ("location_id" in question_fields.keys() and
        any(field in ["country_code", "state", "postcode", "suburb"]
            for field in question_fields.keys())):
        return {"error": "When providing an existing location_id, "
                "don't include any other location fields."}, 400

    # Check that the country exists
    if not Country.query.get(question_fields["country_code"].upper()):
        return {"error": "The country code "
                f"'{question_fields['country_code'].upper()}' "
                "could not be found. Check /countries for a "
                "list of valid country codes."}, 404

    # Set the location to provided location_id or add a new location
    if "location_id" in question_fields.keys():
        # Check if location_id is in database
        if Location.query.get(question_fields["location_id"]):
            found_location = True
            found_location_id = question_fields["location_id"]
        else:
            return location_not_found()

    # Construct a new Location instance
    else:
        new_location = Location(
            country_code=question_fields["country_code"].upper(),
            state=question_fields["state"].title(),
            postcode=question_fields["postcode"].title(),
            suburb=question_fields["suburb"].title()
        )
        # Prevent duplicate locations
        # Check if the provided location fields match an existing location
        found_location = duplicate_exists(
            new_location, Location, ["location_id"])
        # Add the new location if it doesn't exist (outside AU)
        if not found_location:
            if question_fields["country_code"].upper() != "AU":
                db.session.add(new_location)
                db.session.commit()
                new_location_id = new_location.location_id
            else:
                return location_not_found()
        # Assign the found location_id to the new question
        else:
            found_location_id = found_location.location_id

    # Make sure the post has an existing category_id or category_name
    if (not any(field in ["category_id", "category_name"]
                for field in question_fields.keys()) or
        all(field in question_fields.keys()
                    for field in ["category_id", "category_name"])
        ):
        return {"error": "You must provide a category_id "
                "OR category_name, but not both. Visit the /categories "
                "endpoint for a list of valid categories."}, 400
    if "category_id" in question_fields.keys():
        if Category.query.get(question_fields["category_id"]):
            found_category_id = question_fields["category_id"]
        else:
            return {"error": "The given category_id was not found. "
                    "Visit the /categories endpoint for a list of "
                    "valid categories"}, 404
    elif "category_name" in question_fields.keys():
        category = Category.query.filter_by(
            category_name=question_fields["category_name"].title()).first()
        if category:
            found_category_id = category.category_id
        else:
            return {"error": "The given category_name was not found. "
                    "Visit the /categories endpoint for a list of "
                    "valid categories"}, 404

    # Make sure the post has a question body
    if "question" not in question_fields.keys():
        return {"error": "The new question must have a question field."}, 400
    # Question body must be at least 20 characters long
    if len(question_fields["question"]) < 20:
        return {"error": "Your question must be at "
                "least 20 characters."}, 400

    # Construct the question object from fields and add it to the database
    new_question = Question(
        user_id=get_logged_in_user(),
        location_id=found_location_id if found_location else new_location_id,
        category_id=found_category_id,
        date_time=current_datetime(),
        body=question_fields["question"]
    )
    db.session.add(new_question)
    db.session.commit()

    question_snippet = (new_question.body[0:30] if len(new_question.body) > 30
                        else new_question.body)

    return {"success": f"Your question '{question_snippet}...' was posted under "
            f"the {new_question.category.category_name} category for "
            f"{new_question.location.suburb} "
            f"({new_question.location.postcode}), "
            f"{new_question.location.state}, "
            f"{new_question.location.country.country}. "
            f"View it at: /questions/{new_question.question_id}",
            "question_id": new_question.question_id}, 201


@ questions.post("/<question_id>/answer")
@jwt_required()
def post_answer(question_id):
    """ Post an answer to a question by id """
    # Get the answer post fields
    answer_fields = answer_schema.load(request.json, partial=["body"])

    # Construct the new answer object and add it to the database
    new_answer = Answer(
        user_id=get_logged_in_user(),
        question_id=int(question_id),
        parent_id=(
            answer_fields["parent_id"] if "parent_id" in answer_fields
            else None),
        date_time=current_datetime(),
        body=answer_fields["answer"]
    )
    db.session.add(new_answer)
    db.session.commit()

    answer_snippet = (new_answer.body[0:30] if len(
        new_answer.body) > 30 else new_answer.body)

    return {"success": f"Your reply '{answer_snippet}...' was posted under "
            f"question {question_id}. View it here: "
            f"/questions/{question_id}/answers/{new_answer.answer_id}"}, 201


# Return any other validation errors that are raised
@ questions.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
