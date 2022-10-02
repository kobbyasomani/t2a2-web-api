from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app import db, bcrypt
from app.models.user import User
from app.schemas.user_schema import (
    user_schema, user_private_schema, user_update_schema, users_schema)


users = Blueprint("users", __name__, url_prefix="/users")


def find_user(id):
    """ Find a user in the database by user_id or username """
    if id.isdigit():
        user = User.query.get(int(id))
    else:
        user = User.query.filter_by(username=id).first()
    return user


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
    user = find_user(id)
    if user:
        # Check if user is viewing their own profile
        if int(get_jwt_identity()) == user.user_id:
            return jsonify(user_private_schema.dump(user))
        else:
            return jsonify(user_schema.dump(user))
    else:
        return ({"error": "The user could not be found. "
                "Please use a valid user id or username."}), 400


@users.put("/<id>/account")
@jwt_required()
def update_user(id):
    """ Update the account details of a user """
    user = find_user(id)
    # Variable for easy access to currently logged-in user
    current_user = int(get_jwt_identity())
    user_fields = user_update_schema.load(
        request.json, partial=["username", "email", "new_password"])
    changes = False

    # Store the current and new password for validation
    password = user_fields["password"] if "password" in user_fields else None
    new_password = (user_fields["new_password"]
                    if "new_password" in user_fields else None)

    # Prevent modificiation of the user_id
    if "user_id" in user_fields:
        return {"error": "The user id cannot be modified."}

    # If the user was found, validate and update details
    if user:
        # Make sure user is editing their own account
        if current_user == user.user_id:
            # Check the password again when editing account details
            if not password:
                return ({"error": "You must enter your password "
                        "to modify account details."}), 403
            if not bcrypt.check_password_hash(user.password, password):
                return {"error": "The password is incorrect."}, 401

            # Check if any account details have changed
            for field in user_fields:
                if field not in ["password", "new_password"]:
                    if user_fields[field] != getattr(user, field):
                        changes = True
                elif field == "new_password":
                    if not bcrypt.check_password_hash(user.password, user_fields[field]):
                        changes = True
                else:
                    pass
            if not changes:
                return {"message": "No user details were changed."}

            # Update user in database with the given field values
            for field in user_fields:
                # Hash new password if password is being changed
                if field == "new_password":
                    user.password = (bcrypt.generate_password_hash(
                        user_fields["new_password"]).decode("utf-8"))
                # Prevent changing password back to old password
                if field == "password":
                    pass
                # Update all other fields
                else:
                    setattr(user, field, user_fields[field])

            db.session.add(user)
            db.session.commit()

            # Return success message and update details
            updated_user_fields = user_private_schema.dump(user)
            return ({"success":
                    f"Your account details"
                    f"{' and password ' if new_password else ' '}"
                    f"have been updated.",
                    "account details": updated_user_fields})

        # Users can only modify their own account details
        else:
            return ({"message": "You're not authorised "
                    "to modify this user account."}, 403)

    # If the user was not found, return an error
    else:
        return ({"error": "The user could not be found. "
                "Please use a valid user id or username."}), 400
