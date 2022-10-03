from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.category import Category
from app.schemas.category_schema import category_schema, categories_schema

categories = Blueprint("categories", __name__, url_prefix="/categories")


@categories.get("/")
def get_categories():
    """ Get a list of all available categories """
    categories = Category.query.all()
    return jsonify(categories_schema.dump(categories))


# Return any other validation errors that are raised
@categories.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400