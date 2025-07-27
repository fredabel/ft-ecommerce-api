from flask import request, jsonify
from app.blueprints.payments import payments_bp
from app.blueprints.payments.schemas import payment_schema, payments_schema
from marshmallow import ValidationError
from app.models import Payment, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@payments_bp.route("/", methods=['POST'])
@token_required
def create_payment():
    try:
        auth0_id = request.jwt_payload['sub']
        qry = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(qry).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404
        payment_data = payment_schema.load(request.json)
        new_payment = Payment(
            order_id=payment_data['order_id'],
            amount=payment_data['amount'],
            payment_method=payment_data['payment_method'],
            payment_status=payment_data['payment_status'],
            currency=payment_data['currency'],
            transaction_id=payment_data.get('transaction_id', '123TR'),
            refunded_amount=payment_data.get('refunded_amount', 0),
        )
        db.session.add(new_payment)
        db.session.commit()
        return jsonify(payment_schema.dump(new_payment)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to create payment", "errors": str(e)}), 500