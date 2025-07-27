from app.models import ProductVariant
from app.extensions import ma
from marshmallow import fields
class ProductVariantSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested('ProductSchema', only=['id', 'name', 'description', 'price'])
    class Meta:
        model = ProductVariant
        include_fk = True
            
product_variant_schema = ProductVariantSchema()
product_variants_schema = ProductVariantSchema(many=True)
