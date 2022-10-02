from app import ma
from marshmallow import fields
from app.models.question import Question


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = True
        # load_only = ["email", "password"]


class QuestionUpdateSchema(QuestionSchema):
    # new_password = fields.String(required=False)
    pass

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)
question_update_schema = QuestionUpdateSchema()
