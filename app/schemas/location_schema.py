from app import ma
from marshmallow import fields
from app.models.location import Location
from app.schemas.country_schema import CountrySchema


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        include_fk = True
        load_only = ["country_code"]
    country = fields.Nested(CountrySchema)


location_schema = LocationSchema()
