from app.models import Order
from app.extensions import ma
from marshmallow import fields
class OrderSchema(ma.SQLAlchemyAutoSchema):
    order_items = fields.Nested("OrderItemSchema", many=True, exclude=["order"])
    user = fields.Nested("UserSchema")
    cart = fields.Nested("CartSchema")
    shipping_info = fields.Nested("ShippingDetailsSchema", exclude=["order"])
    payments = fields.Nested("PaymentSchema", many=True)
    discount = fields.Nested("DiscountSchema")
    class Meta:
        model = Order
        include_fk = True
            
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
