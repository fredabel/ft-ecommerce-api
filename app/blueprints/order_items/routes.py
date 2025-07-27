from flask import request, jsonify
from app.blueprints.order_items import order_items_bp
from app.blueprints.order_items.schemas import order_item_schema, order_items_schema
from marshmallow import ValidationError
from app.models import OrderItem, Order, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@order_items_bp.route("/", methods=['POST'])
@token_required
def create_order_item():
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Assuming order item data is sent in the request body
        order_item_data = order_item_schema.load(request.json)
        new_order_item = OrderItem(
            order_id=order_item_data['order_id'],
            product_id=order_item_data['product_id'],
            # variant_id=order_item_data.get('variant_id'),  # Optional field
            quantity=order_item_data.get('quantity', 1),  # Default to 1 if not provided
            unit_price=order_item_data['unit_price'],
            subtotal= order_item_data['subtotal'],
            discount= order_item_data.get('discount', 0),  # Optional field
        )
        db.session.add(new_order_item)
        db.session.commit()
        return jsonify({"status": "success", "message": "Order item created successfully", "order_item": order_item_schema.dump(new_order_item)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to create order item", "errors": str(e)}), 500