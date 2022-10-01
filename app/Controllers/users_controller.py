from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db
from app.models.user import User
from app.schemas.user_schema import (
    user_schema, user_schema_private,users_schema)


users = Blueprint("users", __name__, url_prefix="/users")


@users.get("/")
@jwt_required()
def get_users():
    """ Return a list of all users """
    users_list = User.query.all()
    return jsonify(users_schema.dump(users_list))


@users.get("/<id>")
@jwt_required()
def get_user(id):
    """ Return a specific user by user_id or username """
    if id.isdigit():
        user = User.query.get(int(id))
    else:
        user = User.query.filter_by(username=id).first()

    if user:
        if int(get_jwt_identity()) == user.user_id:
            return jsonify(user_schema_private.dump(user))
        else:
            return jsonify(user_schema.dump(user))
    else:
        return ({"error": "The user could not be found. "
                "Please use a valid user id or username."})
