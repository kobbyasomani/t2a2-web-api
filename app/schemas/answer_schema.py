from app import ma
from marshmallow import fields
from app.models.answer import Answer


class AnswerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Answer
        include_fk = True


answer_schema = AnswerSchema()
answers_schema = AnswerSchema(many=True)
