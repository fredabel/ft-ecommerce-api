from app.models import WishList
from app.extensions import ma
from marshmallow import fields
class WishListSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested("ProductSchema")
    user = fields.Nested("UserSchema")
    class Meta:
        model = WishList
        include_fk = True

wishlist_schema = WishListSchema()
wishlists_schema = WishListSchema(many=True)
