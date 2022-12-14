from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.utils import (
    duplicate_exists, current_datetime, record_not_found,
    unauthorised_editor, get_logged_in_user)
from app import db
from app.models.question import Question
from app.models.country import Country
from app.models.location import Location
from app.models.category import Category
from app.models.user import User
from app.models.answer import Answer
from app.schemas.question_schema import (
    question_details_schema,
    question_update_schema, questions_schema, question_post_schema)
from app.schemas.answer_schema import answer_schema


questions = Blueprint("questions", __name__, url_prefix="/questions")


def show_questions_list(questions_list):
    """ Returns a list of questions from a given query object if any
    exist, otherwise returns an error message """
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
        # Turn the arguments into a dictionary
        filter_list = request.args.to_dict()
        # Placholder dict for different table filters
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
        # If there are no query filters, get all questions and show them
        questions_list = Question.query.all()
        return show_questions_list(questions_list)


@questions.get("/<id>")
def get_question(id):
    """ Return a specific question by id with all of its answers """
    # Make sure id is an integer, else return custom error message
    if not id.isdigit():
        return {"error": "The question_id must be an integer. "}, 400

    # Get the question form the database by id
    question = Question.query.get(id)

    # If a matching question is found, return it
    if question:
        return jsonify(question_details_schema.dump(question))
    else:
        return {"error": "A question with that id was not found."}, 404


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

    # Set the location to provided location_id or add a new location
    if "location_id" in question_fields.keys():
        # Check if location_id is in database
        if Location.query.get(question_fields["location_id"]):
            found_location = True
            found_location_id = question_fields["location_id"]
        else:
            return record_not_found("location")

    # Construct a new Location instance
    else:
        # Check that the country exists
        if not Country.query.get(question_fields["country_code"].upper()):
            return {"error": "The country code "
                    f"'{question_fields['country_code'].upper()}' "
                    "could not be found. Check /countries for a "
                    "list of valid country codes."}, 404

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
                return record_not_found("location")

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

    # If searching by category_id, search by primary key
    if "category_id" in question_fields.keys():
        if Category.query.get(question_fields["category_id"]):
            found_category_id = question_fields["category_id"]
        else:
            return {"error": "The given category_id was not found. "
                    "Visit the /categories endpoint for a list of "
                    "valid categories"}, 404

    # If searching by category_name, filter by category_name
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

    # Add a snippet of the new question to the response
    question_snippet = (new_question.body[0:30] if len(new_question.body) > 30
                        else new_question.body)

    # Return a success message with the path to the new question
    return {"success": f"Your question '{question_snippet}...' was posted under "
            f"the {new_question.category.category_name} category for "
            f"{new_question.location.suburb} "
            f"({new_question.location.postcode}), "
            f"{new_question.location.state}, "
            f"{new_question.location.country.country}. "
            f"View it at: /questions/{new_question.question_id}",
            "question_id": new_question.question_id}, 201


@questions.put("/<int:question_id>/edit")
@jwt_required()
def edit_question(question_id):
    """ Edit an existing question """
    # Get the question post fields and the question to update
    question_fields = question_update_schema.load(request.json, partial=True)
    question = Question.query.get(question_id)

    # Make sure there is a question field in the request
    if "question" not in question_fields:
        return {"error": "You must provide a question field."}, 400

    # Check if question exists in the database
    if not question:
        return record_not_found("question")
    else:
        # Make sure user is editing their own question
        if get_logged_in_user() == question.user_id:
            # Check if question body has been changed
            if question_fields["question"] == question.body:
                return {"message": "Your question has not been modified."}
            else:
                # Update the record in the database and commit
                question.body = question_fields["question"]
                db.session.add(question)
                db.session.commit()
                return {"success": "Your question was edited. View it here: "
                        f"/questions/{question_id}"}
        else:
            return unauthorised_editor("question")


@questions.post("/<int:question_id>/answer")
@jwt_required()
def post_answer(question_id):
    """ Post an answer to a question by id """
    # Get the answer post fields
    answer_fields = answer_schema.load(request.json, partial=["body", "user_id"])
    print(type(answer_fields))

    # Check if question exists in the database
    if not Question.query.get(question_id):
        return record_not_found("question")

    # If the answer is a reply to another answer, check if parent exists
    if "parent_id" in answer_fields:
        if not Answer.query.get(answer_fields["parent_id"]):
            return {"error": "The answer you are attempting to repy to "
                    "could not be found"}, 404

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
    # Prevent duplicate answers
    existing_answer = duplicate_exists(
        new_answer, Answer, ["answer_id", "date_time"])
    if not existing_answer:
        db.session.add(new_answer)
        db.session.commit()
    else:
        return {"message": "This answer has already been "
                "posted for this question. View it here: "
                f"/answers/{existing_answer.answer_id}"}

    # Add a snippet of the new answer to the response
    answer_snippet = (new_answer.body[0:30] if len(
        new_answer.body) > 30 else new_answer.body)

    # Return a success message with the path to the new answer
    return {"success": f"Your reply '{answer_snippet}...' was posted under "
            f"question {question_id}. View it here: "
            f"/answers/{new_answer.answer_id}"}, 201


@questions.delete("/<int:question_id>/delete")
@jwt_required()
def delete_question(question_id):
    """ Delete a question by id """
    question = Question.query.get(question_id)

    # Check if the question exists
    if not question:
        return record_not_found("question")

    # Check if the user authored the question
    if get_logged_in_user() == question.user_id:

        # Delete the question from the database
        db.session.delete(question)
        db.session.commit()
        return {"success": f"Question {question.question_id} was deleted."}
    else:
        return unauthorised_editor("question")


# Return any other validation errors that are raised
@questions.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
