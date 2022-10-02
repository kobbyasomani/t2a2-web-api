from app import ma
from marshmallow import fields
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["email", "password"]


class UserPrivateSchema(UserSchema):
    class Meta:
        model = User
        include_fk = True
        load_only = ["password"]


class UserUpdateSchema(UserPrivateSchema):
    new_password = fields.String(required=False)


user_schema = UserSchema()
user_private_schema = UserPrivateSchema()
user_update_schema = UserUpdateSchema()
users_schema = UserSchema(many=True)
