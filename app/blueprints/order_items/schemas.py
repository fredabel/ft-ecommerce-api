from app.models import OrderItem
from app.extensions import ma
from marshmallow import fields
class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    order = fields.Nested('OrderSchema',only=['id', 'subtotal_amount', 'tax_amount', 'shipping_amount', 'total_amount'])
    product = fields.Nested("ProductSchema")
    variant = fields.Nested("ProductVariantSchema")
    class Meta:
        model = OrderItem
        include_fk = True
            
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
