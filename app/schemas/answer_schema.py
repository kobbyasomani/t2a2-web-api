from app import ma
from marshmallow import fields, validate
from app.models.answer import Answer


class AnswerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Answer
        include_fk = True
        dump_only = ["user_id", "question_id", "date_time", "body"]
    answer = fields.String(required=True, validate=validate.Length(min=20))


answer_schema = AnswerSchema()
answers_schema = AnswerSchema(many=True)
