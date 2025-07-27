from app.models import ShippingDetails
from app.extensions import ma
from marshmallow import fields
class ShippingDetailsSchema(ma.SQLAlchemyAutoSchema):
    order = fields.Nested("OrderSchema", exclude=("shipping_info",), dump_only=True)
    class Meta:
        model = ShippingDetails
        include_fk = True
            
shipping_detail_schema = ShippingDetailsSchema()
shipping_details_schema = ShippingDetailsSchema(many=True)
