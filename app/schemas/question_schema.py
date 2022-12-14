from app import ma
from marshmallow import fields, validate
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
    author = fields.Nested(UserSchema())
    category = fields.Nested(CategorySchema(only=["category_id", "category_name"]))
    location = fields.Nested(LocationSchema())


class QuestionDetailsSchema(QuestionSchema):
    """ View a question with all of its replies """
    answers = fields.Nested(AnswerSchema(many=True))
    category = fields.Nested(CategorySchema())


class QuestionPostSchema(QuestionSchema):
    location_id = fields.Integer(required=True)
    country_code = fields.String(
        required=True, validate=validate.Length(equal=2))
    state = fields.String(required=True)
    postcode = fields.String(required=True)
    suburb = fields.String(required=True)
    category_id = fields.Integer(required=True)
    category_name = fields.String(required=True)
    question = fields.String(required=True, validate=validate.Length(min=20))


class QuestionUpdateSchema(QuestionSchema):
    question = fields.String(required=True, validate=validate.Length(min=20))


question_schema = QuestionSchema()
question_details_schema = QuestionDetailsSchema()
questions_details_schema = QuestionDetailsSchema(many=True)
questions_schema = QuestionSchema(many=True)
question_post_schema = QuestionPostSchema()
question_update_schema = QuestionUpdateSchema()
