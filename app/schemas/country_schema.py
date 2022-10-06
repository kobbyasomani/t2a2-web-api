from app import ma
from marshmallow import fields
from app.models.country import Country


class CountrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Country
        include_fk = True