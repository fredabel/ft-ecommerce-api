from app.models import User
from app.extensions import ma
from marshmallow import fields
class UserSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True, required=False)
    class Meta:
        model = User
            
user_schema = UserSchema()
users_schema = UserSchema(many=True)
login_schema = UserSchema(exclude=["full_name","phone"])