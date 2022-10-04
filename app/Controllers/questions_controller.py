from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app import db
from app.models.question import Question
from app.models.location import Location
from app.models.category import Category
from app.models.user import User
from app.schemas.question_schema import (
    question_schema, question_details_schema,
    question_update_schema, questions_schema, question_post_schema)
from app.controllers.users_controller import find_user, get_logged_in_user


questions = Blueprint("questions", __name__, url_prefix="/questions")


def show_questions_list(questions_list):
    if questions_list:
        return jsonify(questions_schema.dump(questions_list))
    else:
        return {"message": "No matching questions were found."}, 404


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

        # Add the filter to relevant subquery filter list
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
            return ({"error": "You can only filter Questions using "
                    "the following attributes in your query string: "
                    f"{filterable_attributes}. Filters using the _id "
                    "suffix format must be integers. country_code must "
                    "be supplied in two-letter ISO format (e.g., AU "
                    "for Australia)."}), 400
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
    print(type(question_fields))

    # # Make sure location_id, and category_id and question are supplied
    # for key in question_fields.keys():
    #     if (not key in ["location_id", "category_id", "question"]
    #             or len(question_fields) < 3):
    #         return ({"error": "You must provide a location_id (integer)"
    #                 ", category_id (integer), and question (string) to"
    #                 " post a new question."}), 400

    # Make sure the post has a location

    # Make sure the post has a category

    # Make sure the post has a question body

    # Construct the question object and add it to the database
    new_question = Question(
        user_id=get_logged_in_user(),
        location_id=question_fields["location_id"],
        category_id=question_fields["category_id"],
        date_time=datetime.now(timezone.utc),
        body=question_fields["question"]
    )
    db.session.add(new_question)
    db.session.commit()

    return ({"success": f"Your question '{new_question.body}' was posted in "
            f"{new_question.category.category_name}."}, 201)


@questions.post("/<question_id>/answer")
def post_answer(question_id):
    """ Post an answer to a squestion by id """
    # Get the answer post fields

    # Construct the answer object and add it to the dataabse

# Return any other validation errors that are raised


@questions.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
