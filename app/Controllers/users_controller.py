from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app import db
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema


users = Blueprint("users", __name__, url_prefix="/users")


@users.get("/")
def get_users():
    """ Return a list of all users """
    users_list = User.query.all()
    return jsonify(users_schema.dump(users_list))


@users.get("/<id>")
def get_user(id):
    """ Return a specific user by user_id or username """
    if id.isdigit():
        user = User.query.get(int(id))
    else:
        user = User.query.filter_by(username=id).first()

    if user:
        return jsonify(user_schema.dump(user))
    else:
        return ({"error": "The user could not be found. "
                "Please use a valid user id or username."})
