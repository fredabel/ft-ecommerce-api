from app.models import Cart
from app.extensions import ma
from marshmallow import fields

class CartSchema(ma.SQLAlchemyAutoSchema):
    cart_items = fields.Nested("CartItemSchema", many=True)
    user = fields.Nested("UserSchema")
    class Meta:
        model = Cart
        include_fk = True
cart_schema = CartSchema()
carts_schema = CartSchema(many=True)