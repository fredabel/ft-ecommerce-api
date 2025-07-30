from flask import request, jsonify
from app.blueprints.payments import payments_bp
from app.blueprints.payments.schemas import payment_schema, payments_schema
from marshmallow import ValidationError
from app.models import Payment, User, Order, OrderItem, Cart, CartItem,  db
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
        
        payload = request.json
        
        payment_status = payload.get('payment_status')
        payment_intent = payload.get('payment_intent')
        payment_method = payload.get('payment_method')
        currency = payload.get('currency')
        order_id = payload.get('order_id')
        
        #Validate Order Details
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        new_payment = Payment(
            order_id=order_id,
            amount= order.total_amount,
            payment_intent_id = payment_intent,
            payment_method=payment_method,
            payment_status=payment_status,
            currency=currency,
            transaction_id=payment_intent,
            refunded_amount=payload.get('refunded_amount', 0),
        )
        db.session.add(new_payment)
        
        # Update Order Details
        order.order_status = payment_status
        
        # Remove cart items that are now in order items
        cart_id = order.cart_id
        if cart_id:
            # Get all product_ids in this order
            ordered_product_ids = [item.product_id for item in order.order_items]
            # Delete cart items for these products in this cart
            db.session.query(CartItem).filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id.in_(ordered_product_ids)
            ).delete(synchronize_session=False)
            
        db.session.commit()
        return jsonify(payment_schema.dump(new_payment)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to create payment", "errors": str(e)}), 500