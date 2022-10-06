from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app import db
from app.models.answer import Answer
from app.schemas.answer_schema import answer_schema, answers_schema
from app.utils import (
    record_not_found, get_logged_in_user, unauthorised_editor)


answers = Blueprint("answers", __name__, url_prefix="/answers")


@answers.get("/<int:id>")
def get_answer(id):
    """ Get an answer by answer_id """
    answer = Answer.query.get(id)

    # Check if answer exists
    if answer:
        return answer_schema.dump(answer)
    else:
        return record_not_found("answer")


@answers.put("/<int:id>/edit")
@jwt_required()
def edit_answer(id):
    """ Update an answer by answer_id """
    answer_fields = answer_schema.load(request.json, partial=["body"])
    answer = Answer.query.get(id)

    # Check if answer exists
    if answer:
        # Check if user is the author of the answer
        if not get_logged_in_user() == answer.user_id:
            return unauthorised_editor("answer")
        else:
            # Check if answer has been modified
            if answer_fields["answer"] == answer.body:
                return {"message": "The answer has not been modified."}
            # Update the answer
            answer.body = answer_fields["answer"]
            db.session.add(answer)
            db.session.commit()
            return {"success": "Your answer was edited. View it here: "
                    f"/answers/{answer.answer_id}"}
    else:
        return record_not_found("answer")


# Return any other validation errors that are raised
@answers.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
