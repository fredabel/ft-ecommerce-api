from app.models import Address
from app.extensions import ma
from marshmallow import fields
class AddressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        include_fk = True
            
address_schema = AddressSchema()
addresses_schema = AddressSchema(many=True)
