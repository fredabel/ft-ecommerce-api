from app.models import SerializedProduct
from app.extensions import ma
from marshmallow import fields

class SerializedProductSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested("ProductSchema")
  
    class Meta:
        model = SerializedProduct
        include_fk = True

serialized_product_schema = SerializedProductSchema()
serialized_products_schema = SerializedProductSchema(many=True)
