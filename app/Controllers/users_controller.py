from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema


users = Blueprint("users", __name__, url_prefix="/users")


@users.get("/")
def get_users():
    """ Return a list of all users """
    users_list = User.query.all()
    return jsonify(users_schema.dump(users_list))