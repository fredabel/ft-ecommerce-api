from app.models import Product
from app.extensions import ma
from marshmallow import fields

class ProductSchema(ma.SQLAlchemyAutoSchema):
    category = fields.Nested("CategorySchema")
    serial_products = fields.Nested("SerializedProductSchema", many=True, exclude=["product"])

    class Meta:
        model = Product
        include_fk = True
     
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)