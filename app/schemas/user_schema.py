from app import ma
from marshmallow import fields
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["email", "password"]

class UserSchemaPrivate(UserSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["password"]


user_schema = UserSchema()
user_schema_private = UserSchemaPrivate()
users_schema = UserSchema(many=True)
