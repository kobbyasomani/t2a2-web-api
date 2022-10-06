from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app import db
from app.models.answer import Answer
from app.models.recommendation import Recommendation
from app.schemas.answer_schema import (
    answer_schema, answer_details_schema, answers_schema)
from app.utils import (
    duplicate_exists, record_not_found, get_logged_in_user, unauthorised_editor)


answers = Blueprint("answers", __name__, url_prefix="/answers")


@answers.get("/")
def get_answers():
    """ Get all answers posted to all questions """
    answers_list = Answer.query.all()

    if answers_list:
        return answers_schema.dump(answers_list)
    else:
        return {"message": "There are no answers posted yet."}


@answers.get("/<int:id>")
def get_answer(id):
    """ Get an answer by answer_id """
    answer = Answer.query.get(id)

    # Check if answer exists
    if answer:
        return answer_details_schema.dump(answer)
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


@answers.delete("/<int:id>/delete")
@jwt_required()
def delete_question(id):
    """ Delete an answer by id """
    answer = Answer.query.get(id)

    # Check if the answer exists
    if not answer:
        return record_not_found("answer")

    # Check if the user authored the answer
    if get_logged_in_user() == answer.user_id:

        # Delete the answer from the database
        db.session.delete(answer)
        db.session.commit()
        return {"success": f"Answer {answer.answer_id} was deleted "
                f"from Question {answer.question_id}. View the question: "
                f"/questions/{answer.question_id}"}
    else:
        return unauthorised_editor("answer")


@answers.post("/<int:id>/<vote_action>")
@jwt_required()
def recommend_answer(id, vote_action):
    """ Vote for an answer as the recommended answer to a question """
    answer = Answer.query.get(id)
    vote = Recommendation.query.filter(
        Recommendation.answer_id == answer.answer_id,
        Recommendation.user_id == get_logged_in_user()
    ).first()

    # Check if the answer exists
    if not answer:
        return record_not_found("answer")

    # The user is adding a new recommendation to an answer
    if vote_action == "vote":
        # Construct the new recommendation
        new_vote = Recommendation(
            answer_id=answer.answer_id,
            user_id=get_logged_in_user()
        )
        # Check if user has recommended this answer already
        if duplicate_exists(new_vote, Recommendation, ["vote_id"]):
            return {"message": "You have already recommended this answer."}
        else:
            # Add the recommendation
            db.session.add(new_vote)
            db.session.commit()
            return {"success": f"You recommended Answer {answer.answer_id} "
                    f"'{answer.body}': "
                    f"/answers/{answer.answer_id} "
                    f"as a good answer to Question {answer.question_id}: "
                    f"/questions/{answer.question_id}"}

    # The user is removing their recommendation from an answer
    elif vote_action == "remove-vote":
        # Check if user has recommended this answer
        if not vote:
            return {"message": "You haven't recommended this answer."}
        else:
            # Make sure user is removing their own recommendation
            if get_logged_in_user() != vote.user_id:
                return unauthorised_editor("recommendation")
            else:
                # Remove the recommendation
                db.session.delete(vote)
                db.session.commit()
                return {"success": f"You removed your recommendation from "
                        f"Answer {answer.answer_id} '{answer.body}': "
                        f"/answers/{answer.answer_id} "
                        f"of Question {answer.question_id}: "
                        f"/questions/{answer.question_id}"}


# Return any other validation errors that are raised
@answers.errorhandler(ValidationError)
def register_validation_error(error):
    return error.messages, 400
