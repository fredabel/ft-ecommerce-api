from app.models import Review
from app.extensions import ma
from marshmallow import fields
class ReviewSchema(ma.SQLAlchemyAutoSchema):
    product = fields.Nested("ProductSchema")
    user = fields.Nested("UserSchema")
    class Meta:
        model = Review
        include_fk = True
            
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
