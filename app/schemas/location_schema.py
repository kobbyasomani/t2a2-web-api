from app import ma
from marshmallow import fields
from app.models.location import Location


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        include_fk = True


location_schema = LocationSchema()
