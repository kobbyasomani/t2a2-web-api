from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.question import Question
from app.models.location import Location
from app.models.postcode import Postcode
from app.models.category import Category
from app.models.user import User
from app.schemas.question_schema import (
    question_schema, question_details_schema,
    question_update_schema, questions_schema)


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
        "country_id",
        "country",
        "state",
        "city",
        "postcode",
        "suburb",
    ]

    # Check for a query string to filter results
    if request.query_string:
        filter_list = request.args.to_dict()
        subquery_filters = {
            "question": {},
            "user": {},
            "category": {},
            "location": {},
            "postcode": {},
            "country": {}
        }

        # Check if supplied filter attributes can be used
        valid_filters = True
        for key, value in filter_list.items():
            if key not in filterable_attributes:
                valid_filters = False
            # Convert inputs to match database keys
            if key in ["category_name", "country", "state", "city", "suburb"]:
                filter_list[key] = value.title()

        # Add the filter to relevant subquery filter list
        for key, value in filter_list.items():
            if key in ["country_id", "suburb", "postcode"]:
                subquery_filters["location"][key] = filter_list[key]
            elif key in ["city", "state"]:
                subquery_filters["postcode"][key] = filter_list[key]
            elif key in ["country"]:
                subquery_filters["country"]["name"] = filter_list[key]
            elif key in ["username"]:
                subquery_filters["user"][key] = filter_list[key]
            elif key in ["category_name"]:
                subquery_filters["category"][key] = filter_list[key]
            else:
                subquery_filters["question"][key] = filter_list[key]

        # Filter questions list using request arguments
        if valid_filters:
            questions_list = Question.query.filter_by(
                **subquery_filters["question"]).join(
                User.query.filter_by(**subquery_filters["user"])).join(
                    Location.query.filter_by(
                        **subquery_filters["location"])).join(
                    Category.query.filter_by(
                        **subquery_filters["category"])).join(
                    Postcode.query.filter_by(
                        **subquery_filters["postcode"])).join(
                            Postcode.country
            ).all()

            # Query ran successfully
            return show_questions_list(questions_list)

        # One or more filters passed as URL query arguments were invalid
        else:
            return ({"error": "You can only filter Questions using "
                    "the following attributes in your query string: "
                    f"{filterable_attributes}. Filters using the _id "
                    "suffix format must be integers. country_id must "
                    "be supplied in two-letter ISO format (e.g., AU "
                    "for Australia)."}), 400
    else:
        questions_list = Question.query.all()
        return show_questions_list(questions)


@questions.get("/<int:id>")
def get_question(id):
    """ Return a specific question by id with all of its answers """
    question = Question.query.get(id)
    if question:
        return jsonify(question_details_schema.dump(question))
    else:
        return {"message": "A question with that id was not found."}, 404


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
            Question.category).filter_by(category_name=id.title()
        ).all()

    return show_questions_list(questions_list)


# Return any other validation errors that are raised
@questions.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400