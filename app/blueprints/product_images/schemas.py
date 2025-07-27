from app.models import ProductImage
from app.extensions import ma
from marshmallow import fields
class ProductImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImage
        include_fk = True
            
product_image_schema = ProductImageSchema()
product_images_schema = ProductImageSchema(many=True)
