from app.models import Payment
from app.extensions import ma
from marshmallow import fields
class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        include_fk = True
            
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
