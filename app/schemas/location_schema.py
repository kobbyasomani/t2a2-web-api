from app import ma
from marshmallow import fields
from app.models.location import Location
from app.schemas.postcode_schema import PostcodeSchema


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        include_fk = True
    code = fields.Nested(PostcodeSchema, only=("city", "state"), data_key="region")


location_schema = LocationSchema()
