from app import ma
from marshmallow import fields
from app.models.question import Question
from app.schemas.user_schema import UserSchema
from app.schemas.category_schema import CategorySchema
from app.schemas.location_schema import LocationSchema


class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_fk = True
        load_only = ["category_id", "user_id", "location_id"]
    author = fields.Nested(UserSchema())
    category = fields.Nested(CategorySchema())
    location = fields.Nested(LocationSchema())


class QuestionUpdateSchema(QuestionSchema):
    # update_only_field = fields.String(required=False)
    pass


question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)
question_update_schema = QuestionUpdateSchema()
