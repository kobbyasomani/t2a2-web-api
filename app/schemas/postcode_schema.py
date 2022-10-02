from app import ma
from marshmallow import fields
from app.models.postcode import Postcode


class PostcodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Postcode
        include_fk = True


postcode_schema = PostcodeSchema()
