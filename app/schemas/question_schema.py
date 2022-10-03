from app import ma
from marshmallow import fields
from app.models.question import Question
from app.schemas.user_schema import UserSchema
from app.schemas.category_schema import CategorySchema
from app.schemas.location_schema import LocationSchema
from app.schemas.answer_schema import AnswerSchema


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = True
        load_only = ["category_id", "user_id", "location_id"]
        dump_only = ["date_time"]
    ordered = True
    author = fields.Nested(UserSchema())
    category = fields.Nested(CategorySchema())
    location = fields.Nested(LocationSchema())


class QuestionDetailsSchema(QuestionSchema):
    """ View a question with all its replies """
    answers = fields.Nested(AnswerSchema(many=True))


class QuestionPostSchema(QuestionSchema):
    location_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    question = fields.String(required=True)


class QuestionUpdateSchema(QuestionSchema):
    # update_only_field = fields.String(required=False)
    pass


question_schema = QuestionSchema()
question_details_schema = QuestionDetailsSchema()
questions_schema = QuestionSchema(many=True)
question_post_schema = QuestionPostSchema()
question_update_schema = QuestionUpdateSchema()
