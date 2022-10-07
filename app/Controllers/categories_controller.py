from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.category import Category
from app.models.question import Question
from app.controllers.questions_controller import show_questions_list
from app.schemas.category_schema import category_schema, categories_schema

categories = Blueprint("categories", __name__, url_prefix="/categories")


@categories.get("/")
def get_categories():
    """ Get a list of all available categories """
    categories = Category.query.all()
    return jsonify(categories_schema.dump(categories))



@categories.get("/<id>")
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



# Return any other validation errors that are raised
@categories.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400