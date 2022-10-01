from app import ma
from marshmallow import fields
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["email", "password"]


user_schema = UserSchema()
users_schema = UserSchema(many=True)
