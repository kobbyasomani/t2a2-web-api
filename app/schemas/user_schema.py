from app import ma
from marshmallow import fields
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["email", "password"]

    def get_questions_count(self, obj):
        """ Return the number of questions posted by user """
        return len(obj.questions)

    def get_answers_count(self, obj):
        """ Return the number of answers posted by user """
        return len(obj.answers)

    def get_votes_count(self, obj):
        """ Return the number of recommendations given by user """
        return len(obj.recommendations)


class UserPrivateSchema(UserSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["password"]
    stat_questions_posted = fields.Method("get_questions_count")
    stat_answers_posted = fields.Method("get_answers_count")
    stat_recommendations_given = fields.Method("get_votes_count")


class UserUpdateSchema(UserPrivateSchema):
    new_password = fields.String(required=False)


class UserDetailsSchema(UserSchema):
    stat_questions_posted = fields.Method("get_questions_count")
    stat_answers_posted = fields.Method("get_answers_count")
    stat_recommendations_given = fields.Method("get_votes_count")


user_schema = UserSchema()
user_details_schema = UserDetailsSchema()
user_private_schema = UserPrivateSchema()
user_update_schema = UserUpdateSchema()
users_schema = UserSchema(many=True)
