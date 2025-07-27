from app.models import Discount
from app.extensions import ma
from marshmallow import fields
class DiscountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discount
            
discount_schema = DiscountSchema()
discounts_schema = DiscountSchema(many=True)
