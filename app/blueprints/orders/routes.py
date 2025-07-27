from flask import request, jsonify
from app.blueprints.orders import orders_bp
from app.blueprints.orders.schemas import order_schema, orders_schema
from marshmallow import ValidationError
from app.models import Order, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@orders_bp.route("/", methods=['POST'])
@token_required
def create_order():
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        print(user.id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
   
        # Assuming order data is sent in the request body
        new_order = Order(
            user_id=user.id,
            cart_id= request.json.get('cart_id'),
            order_number=request.json.get('order_number'),
            subtotal_amount=request.json.get('subtotal_amount', 0.0),
            tax_amount=request.json.get('tax_amount', 0.0),
            shipping_amount=request.json.get('shipping_amount', 0.0),
            total_amount=request.json.get('total_amount', 0.0),
            shipping_address=request.json.get('shipping_address'),
            billing_address=request.json.get('billing_address'),
            discount_id=request.json.get('discount_id'),
            order_date=request.json.get('order_date'),
            order_status=request.json.get('status', 'pending'),
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"status": "success", "message": "Order created successfully", "order": order_schema.dump(new_order)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to create order", "errors": str(e)}), 500