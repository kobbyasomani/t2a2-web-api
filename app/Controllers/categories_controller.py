from flask import Blueprint, jsonify
from marshmallow import ValidationError
from app.models.category import Category
from app.models.question import Question
from app.controllers.questions_controller import show_questions_list
from app.schemas.category_schema import categories_schema

categories = Blueprint("categories", __name__, url_prefix="/categories")


@categories.get("/")
def get_categories():
    """ Get a list of all available categories """
    # Get all categoires form the database
    categories = Category.query.all()
    # Return the list of all categories
    return jsonify(categories_schema.dump(categories))


@categories.get("/<id>")
def get_questions_by_category(id):
    """ Return all questions for a given category name or id """
    # Get all questions from the specified category by category_id
    if id.isdigit():
        questions_list = Question.query.filter(
            Question.category_id == id,
        ).all()

    # Get all questions from the specified category by category_name
    else:
        questions_list = Question.query.join(
            Question.category).filter_by(
                category_name=id.title()
        ).all()
    # Return the list of questions for the category
    return show_questions_list(questions_list)


# Return any other validation errors that are raised
@categories.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
