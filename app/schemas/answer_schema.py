from app import ma
from marshmallow import fields, validate
from app.models.answer import Answer
from app.models.recommendation import Recommendation
from app.schemas.user_schema import UserSchema
from app.schemas.category_schema import CategorySchema


class AnswerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Answer
        include_fk = True
        dump_only = ["user_id", "question_id", "date_time"]
    answer = fields.String(required=True, validate=validate.Length(min=20))
    recommendations = fields.Method("get_recommendation_count")

    def get_recommendation_count(self, obj):
        """ Return the number of recommendations a question has received """
        # obj = Recommendation.query.filter_by(answer_id=obj.user_id).all()
        return len(obj.recommendations)


class AnswerRepliesSchema(AnswerSchema):
    replies = fields.Nested(lambda: AnswerRepliesSchema(many=True))


class AnswerDetailsSchema(AnswerSchema):
    class Meta:
        load_only = ["question_id", "user_id"]
    replies = fields.Nested(AnswerRepliesSchema(many=True))
    author = fields.Nested(UserSchema)
    question = fields.Nested("QuestionSchema", only=["question_id", "body"])
    # recommendations = fields.Nested(RecommendationSchema))


answer_schema = AnswerSchema()
answer_details_schema = AnswerDetailsSchema()
answers_schema = AnswerSchema(many=True)
