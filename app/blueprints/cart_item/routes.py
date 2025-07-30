from flask import request, jsonify
from app.blueprints.cart_item import cart_item_bp
from app.blueprints.cart_item.schemas import cart_item_schema, cart_items_schema
from marshmallow import ValidationError
from app.models import CartItem, Cart, User, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import token_required

# -------------------- Create a Cart Item --------------------
# This route allows the creation of a new cart item.
# Rate limited to 10 requests per hour to prevent spamming.
@cart_item_bp.route("/",methods=['POST'])
@token_required
def create_cart_item():
    try:
        auth0_id = request.jwt_payload['sub']
        data = request.json
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        stmt = select(Cart).where(Cart.user_id == user.id)
        cart = db.session.execute(stmt).scalars().first()
        
        if not cart:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
            
        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == data['product_id']
        )
        cart_item = db.session.execute(stmt).scalars().first()
        
        if cart_item:
            cart_item.quantity += 1 
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=data['product_id'],
                quantity=1
            )
            db.session.add(cart_item)
        db.session.commit()    
        return jsonify({
            "status": "success",
            "message": "Successfully added to cart",
            "cart_item": cart_item_schema.dump(cart_item)
        }), 201
        
    except ValidationError as err:
        return jsonify(err.messages), 400

   
@cart_item_bp.route("/", methods=['GET'])
@token_required
def get_cart_items():
    try:
        cart_id = request.args.get('cart_id', type=int)
        stmt = select(CartItem).where(CartItem.cart_id == cart_id)
        cart_items = db.session.execute(stmt).scalars().all()
        return jsonify(cart_items_schema.dump(cart_items)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@cart_item_bp.route("/<int:id>", methods=['PUT'])
@token_required
def update_cart_item(id):
    try:
        auth0_id = request.jwt_payload['sub']
        data = request.json
        # Find the user
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404


        # Find the cart item by id and make sure it belongs to this cart
        stmt = select(CartItem).where(CartItem.id == id)
        cart_item = db.session.execute(stmt).scalars().first()
        if not cart_item:
            return jsonify({"status": "error", "message": f"Cart item {id} not found in your cart"}), 404

        # Update the quantity (or other fields as needed)
        new_quantity = data.get("quantity")
        if new_quantity is not None and isinstance(new_quantity, int) and new_quantity > 0:
            cart_item.quantity = new_quantity
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": f"Successfully updated cart item {id}",
                "cart_item": cart_item_schema.dump(cart_item)
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid quantity"}), 400

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@cart_item_bp.route("/<int:id>", methods=['DELETE'])
@token_required
def delete_cart_item(id):
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # Find the customer's cart
        stmt = select(Cart).where(Cart.user_id == user.id)
        cart = db.session.execute(stmt).scalars().first()
        
        # Find the cart item by id and make sure it belongs to this cart
        stmt = select(CartItem).where(CartItem.id == id, CartItem.cart_id == cart.id)
        cart_item = db.session.execute(stmt).scalars().first()
        if not cart_item:
            return jsonify({"status": "error", "message": f"Cart item {id} not found in your cart"}), 404

        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"status": "success", "message": f"Successfully deleted cart item {id}"}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
