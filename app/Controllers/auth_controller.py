from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import or_
from app import db, bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app.models.user import User
from app.schemas.user_schema import user_schema


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/register")
def register_user():
    """ Register a new user in the database """
    # Get the request fields
    user_fields = user_schema.load(request.json)

    # Check if a user with the same username or email address
    # already exists in the database
    username = User.query.filter_by(
        username=user_fields["username"]).first()
    email = User.query.filter_by(email=user_fields["email"]).first()

    # Return an error if user already exists or email is already in use
    if username or email:
        result = (
            f"A user with this {'username' if username else ''}"
            f"{' and ' if username and email else ''}"
            f"{'email address' if email else ''} already exists."
        )
        return {"error": result}, 400

    # Create a new user from request fields and hash password
    new_user = User(
        username=user_fields["username"],
        email=user_fields["email"],
        password=(bcrypt.generate_password_hash(
            user_fields["password"]).decode("utf-8"))
    )

    # Add the user to the database and commit
    db.session.add(new_user)
    db.session.commit()
    return {"success": f"The user {new_user.username} was created."}


@auth.post("/login")
def login_user():
    """ Authenticate user and return an access token if successful """
    user_fields = user_schema.load(request.json, partial=True)
    username = user_fields["username"] if "username" in user_fields else None
    email = user_fields["email"] if "email" in user_fields else None
    password = user_fields["password"] if "password" in user_fields else None

    # Check that the provided username or email address exists in database
    if username or email:
        user = User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()
        if not user:
            return {"error": "The user does not exist."}, 400
    else:
        return {"error": "A username or email address is required"}, 400

    # Check provided password
    if not password:
        return {"error": "You must enter a password"}
    if not bcrypt.check_password_hash(user.password, password):
        return {"error": "The password is incorrect."}, 401

    # If user exists and password is correct, issue an access token
    access_token = create_access_token(
        identity=str(user.user_id),
        expires_delta=timedelta(days=1)
    )
    return {"user": user.username, "token": access_token}


# Return any other validation errors that are raised
@auth.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
