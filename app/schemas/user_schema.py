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


class UserSchemaUpdate(UserSchemaPrivate):
    new_password = fields.String(required=False)


user_schema = UserSchema()
user_private_schema = UserSchemaPrivate()
user_update_schema = UserSchemaUpdate()
users_schema = UserSchema(many=True)
