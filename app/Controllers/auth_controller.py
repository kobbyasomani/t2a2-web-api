from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from app import db, bcrypt, jwt
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/register")
def register_user():
    """ Register a new user in the database """
    user_fields = user_schema.load(request.json)

    # Check if a user with the same username or email address
    # already exists in the database
    username = User.query.filter_by(
        username = user_fields["username"]).first()
    email = User.query.filter_by(email = user_fields["email"]).first()
    
    # Return an error if user already exists or email is already in use
    if username or email:
        result = (f"A user with this {'username' if username else ''}"
            f"{' and ' if username and email else ''}"
            f"{'email address' if email else ''} already exists.")
        return {"error": result}, 400

    # Create a new user from request fields and hash password
    new_user = User(
        username=user_fields["username"],
        email=user_fields["email"],
        password=(bcrypt.generate_password_hash(
            user_fields["password"]).decode("utf-8"))
    )

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": f"The user {new_user.username} was created."})
