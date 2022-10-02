from app import ma
from marshmallow import fields
from app.models.category import Category


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_fk = True


category_schema = CategorySchema()
