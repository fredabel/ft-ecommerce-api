from app.models import CartItem
from app.extensions import ma
from marshmallow import fields

class CartItemSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested("ProductSchema")
    class Meta:
        model = CartItem
        include_fk = True  # so it includes cart_id, product_id

cart_item_schema = CartItemSchema()
cart_items_schema = CartItemSchema(many=True)