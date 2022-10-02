from flask import Blueprint, jsonify, request
from app import db
from app.models.question import Question
from app.schemas.question_schema import (
    question_schema, question_update_schema, questions_schema)


questions = Blueprint("questions", __name__, url_prefix="/questions")


@questions.get("/")
def get_questions():
    """ Return all questions """
    questions_list = Question.query.all()
    return jsonify(questions_schema.dump(questions_list))