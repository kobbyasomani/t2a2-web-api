from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app import db, bcrypt
from app.models.user import User
from app.models.question import Question
from app.models.answer import Answer
from app.models.recommendation import Recommendation
from app.schemas.user_schema import (
    user_details_schema, user_private_schema, user_update_schema, users_schema)
from app.schemas.question_schema import questions_schema, questions_details_schema
from app.schemas.answer_schema import answers_schema, answers_details_schema
from app.utils import get_logged_in_user, record_not_found


users = Blueprint("users", __name__, url_prefix="/users")


def find_user(id):
    """ Find a user in the database by user_id or username """
    if id.isdigit():
        user = User.query.get(int(id))
    else:
        user = User.query.filter_by(username=id).first()
    return user


def user_not_found():
    """ Return a 404 response beacause the user could not be found """
    return ({"error": "The user could not be found. "
            "Please use a valid user id or username."}), 404


def unauthorised_action():
    """ Return a 403 response because the user cannot perform this action"""
    return ({"message": "You're not authorised "
            "to delete this user account."}, 403)


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
        if get_logged_in_user() == user.user_id:
            return jsonify(user_private_schema.dump(user))
        else:
            return jsonify(user_details_schema.dump(user))
    else:
        return user_not_found()


@users.put("/<id>/account")
@jwt_required()
def update_user(id):
    """ Update the account details of a user """
    user = find_user(id)
    # Variable for easy access to currently logged-in user
    logged_in_user = get_logged_in_user()
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
        if logged_in_user == user.user_id:
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
            return ({
                "success":
                f"Your account details"
                f"{' and password ' if new_password else ' '}"
                f"have been updated.",
                "account details": updated_user_fields
            })

        # Users can only modify their own account details
        else:
            return unauthorised_action()

    # If the user was not found, return an error
    else:
        return user_not_found()


@users.delete("/<id>/close-account")
@jwt_required()
def delete_user(id):
    """ Delete the user and associated posts """
    user = find_user(id)
    if user:
        # Make sure user is editing their own account
        if get_logged_in_user() == user.user_id:
            db.session.delete(user)
            db.session.commit()

            return {"success": f"Your account {user.username} was removed."}

        # Users can only modify their own account details
        else:
            return unauthorised_action()

    return user_not_found()


@users.get("/<id>/<post_type>")
def get_user_questions(id, post_type):
    """ Return all questions posted by a given user """
    user = find_user(id)

    if user:
        questions_list = Question.query.filter_by(user_id=user.user_id).all()
        answers_list = Answer.query.filter_by(user_id=user.user_id).all()
        recommendations_list = Answer.query.join(
            Answer.recommendations).all()
    else:
        return user_not_found()

    # Return all questions/answers posted by user
    if post_type == "questions":
        if questions_list:
            return questions_schema.dump(questions_list)
        return {"message": f"{user.username} has not posted any "
                "questions yet."}
    elif post_type == "answers":
        if answers_list:
            return answers_schema.dump(answers_list)
        return {"message": f"{user.username} has not posted any answers yet."}
    elif post_type == "q&a":
        if questions_list:
            return questions_details_schema.dump(questions_list)
        return {"message": f"{user.username} has not posted any "
                "questions yet."}
    elif post_type == "recommendations":
        if recommendations_list:
            return answers_schema.dump(recommendations_list)
        return {"message": f"{user.username} has not given any "
                "recommendations yet."}
    else:
        return {"error": f"Visit, /users/{user.username}/questions "
                "for all questions posted by "
                f"{user.username}; /users/{user.username}/answers "
                f"for all answers posted by them; or "
                f"/users/{user.username}/q&a "
                "for their questions with answers included."}


# Return any other validation errors that are raised
@users.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
