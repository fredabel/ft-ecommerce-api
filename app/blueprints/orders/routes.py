from flask import request, jsonify
from app.blueprints.orders import orders_bp
from app.blueprints.orders.schemas import order_schema, orders_schema
from marshmallow import ValidationError
from app.models import Order, OrderItem, Cart, CartItem, Discount, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import  token_required
import random, string, time


@orders_bp.route("/", methods=['POST'])
@token_required
def create_order():
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Find the user's unpaid cart (or use cart_id from request)
        cart_id = request.json.get('cart_id')
        cart = db.session.get(Cart, cart_id)
        if not cart or cart.user_id != user.id:
            return jsonify({"status": "error", "message": "Cart not found or does not belong to user"}), 404
        
        cart_item_ids = request.json.get('cart_item_ids', [])
        if not cart_item_ids:
            return jsonify({"status": "error", "message": "No cart item IDs provided"}), 400

        # Fetch cart items by IDs and ensure they belong to the cart
        cart_items = db.session.query(CartItem).filter(
            CartItem.id.in_(cart_item_ids),
            CartItem.cart_id == cart.id
        ).all()
        
        if not cart_items or len(cart_items) != len(cart_item_ids):
            return jsonify({"status": "error", "message": "Some cart items not found or do not belong to this cart"}), 400
        
        #Generate order number 
        timestamp = int(time.time())  # seconds since epoch
        suffix = random.randint(1000, 9999)
        order_number = f"ORD-{user.id}-{timestamp}-{suffix}"
        
        # Calculate totals from cart items if needed
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        print(subtotal)
        tax = request.json.get('tax_amount', 0)
        shipping = request.json.get('shipping_amount', 0)
        discount_id = request.json.get('discount_id', None)
        discount_amount = request.json.get('discount_amount', 0)
        print(discount_amount)
        discount = 0
        if discount_id:
            # You can add logic to fetch and apply discount here
            pass
        total = subtotal + tax + shipping - discount_amount
        
        # Check for existing pending order for this cart and user
        existing_order = db.session.query(Order).filter_by(
            cart_id=cart.id,
            user_id=user.id,
            order_status='pending'
        ).first()
        
        if existing_order:
            # Update the existing pending order
            existing_order.subtotal_amount = subtotal
            existing_order.tax_amount = tax
            existing_order.discount_amount = discount_amount
            existing_order.shipping_amount = shipping
            existing_order.total_amount = total
            existing_order.shipping_address = request.json.get('shipping_address')
            existing_order.billing_address = request.json.get('billing_address')
            existing_order.discount_id = discount_id
            # existing_order.order_date = request.json.get('order_date')
            existing_order.order_status = request.json.get('status', 'pending')
            
            db.session.query(OrderItem).filter_by(order_id=existing_order.id).delete()
            order_id = existing_order.id
            db.session.commit() 
            order_to_return = existing_order
            
        else:
            new_order = Order(
                user_id=user.id,
                cart_id=cart.id,
                order_number=order_number,  # Or generate one here
                subtotal_amount=subtotal,
                tax_amount=tax,
                shipping_amount=shipping,
                total_amount=total,
                shipping_address=request.json.get('shipping_address'),
                billing_address=request.json.get('billing_address'),
                discount_id=discount_id,
                discount_amount=discount_amount,
                order_date=request.json.get('order_date'),
            )
            db.session.add(new_order)
            db.session.flush()  # Get new_order.id before commit
            order_id=new_order.id
            order_to_return = new_order
        
        # Create order items from cart items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                discount=discount,
                subtotal=cart_item.quantity * cart_item.product.price
            )
            db.session.add(order_item)
        db.session.commit()
        return jsonify({"status": "success", "message": "Order created successfully", "order": order_schema.dump(order_to_return)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to create order", "errors": str(e)}), 500
# @orders_bp.route("/", methods=['POST'])
# @token_required
# def create_order():
#     try:
#         auth0_id = request.jwt_payload['sub']
#         query = select(User).where(User.auth0_id == auth0_id)
#         user = db.session.execute(query).scalars().first()
#         if not user:
#             return jsonify({"status": "error", "message": "User not found"}), 404
   
#         # Assuming order data is sent in the request body
#         new_order = Order(
#             user_id=user.id,
#             cart_id= request.json.get('cart_id'),
#             order_number=request.json.get('order_number'),
#             subtotal_amount=request.json.get('subtotal_amount', 0.0),
#             tax_amount=request.json.get('tax_amount', 0.0),
#             shipping_amount=request.json.get('shipping_amount', 0.0),
#             total_amount=request.json.get('total_amount', 0.0),
#             shipping_address=request.json.get('shipping_address'),
#             billing_address=request.json.get('billing_address'),
#             discount_id=request.json.get('discount_id'),
#             order_date=request.json.get('order_date'),
#             order_status=request.json.get('status', 'pending'),
#         )
#         db.session.add(new_order)
#         db.session.commit()
#         return jsonify({"status": "success", "message": "Order created successfully", "order": order_schema.dump(new_order)}), 201
#     except ValidationError as err:
#         return jsonify(err.messages), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": "Failed to create order", "errors": str(e)}), 500
    
@orders_bp.route('/my_orders', methods=['GET'])
@token_required
def get_my_orders():
    try:
        auth0_id = request.jwt_payload['sub']
        stmt = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(stmt).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        stmt = select(Order).where(Order.user_id == user.id)
        orders = db.session.execute(stmt).scalars().all()
        return jsonify(orders_schema.dump(orders)), 200 
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get orders", "errors": str(e)}), 500
    
@orders_bp.route('/my_orders', methods=['PUT'])
@token_required
def update_my_order():
    try:
        auth0_id = request.jwt_payload['sub']
        stmt = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(stmt).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        order_id = request.json.get('order_id')
        print(order_id)
        
        stmt = select(Order).where(Order.id == order_id, Order.order_status == 'pending')
        order = db.session.execute(stmt).scalars().first()
        if not order:
            return jsonify({"status": "error", "message": "Order not found"}), 404
        
        discount_id = request.json.get('discount_id', None)
        #Get Discount Details
        discount = db.session.get(Discount, discount_id)
        #Compute
        if discount.discount_type == 'fixed':
            discount_amount = order.total_amount - discount.discount_value
        else:
            discount_amount = order.total_amount * discount.discount_value
            
        order.discount_id = discount_id
        order.discount_amount = discount_amount
        
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Order updated successfully", "order": order_schema.dump(order)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get orders", "errors": str(e)}), 500