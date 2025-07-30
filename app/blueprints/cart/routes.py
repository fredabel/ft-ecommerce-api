from flask import request, jsonify
from app.blueprints.cart import cart_bp
from app.blueprints.cart.schemas import cart_schema, carts_schema
from marshmallow import ValidationError
from app.models import Cart, User, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
from app.utils.util import token_required
import stripe
from dotenv import load_dotenv
import os

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@cart_bp.route("/",methods=['POST'])
@token_required
def create_cart():
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_cart = Cart(user_id=user.id)
    db.session.add(new_cart)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Successfully created a new cart",
        "cart": cart_schema.dump(new_cart)
    }), 201

@cart_bp.route("/", methods=['GET'])
def get_cart():
    stmt = select(Cart)
    result = db.session.execute(stmt)
    cart = result.scalars().first()
    return jsonify(cart_schema.dump(cart)), 200

#Cart Unpaid
@cart_bp.route("/my_cart", methods=['GET'])
@token_required
def get_my_cart():
    
    auth0_id = request.jwt_payload['sub']
    query = select(User).where(User.auth0_id == auth0_id)
    user = db.session.execute(query).scalars().first()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    stmt = select(Cart).where(Cart.user_id == user.id)
    cart = db.session.execute(stmt).scalars().first()
    return jsonify(cart_schema.dump(cart)), 200


@cart_bp.route("/update_cart/<int:id>", methods=['PUT'])
@token_required
def update_my_cart(id):
    try:
        
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error","message":"User not found"}), 404
        
        cart = db.session.get(Cart, id)
        if not cart:
            return jsonify({"status": "error","message":"Cart not found"}), 404
        
        for field, value in request.json.items():
            setattr(cart, field, value)
            
        db.session.commit()   
        return jsonify({"status": "success","message":"Successfully Updated!"}), 200
    
    except ValidationError as err:
        return jsonify(err.messages), 400

@cart_bp.route("/<int:id>", methods=['DELETE'])
@token_required
def delete_cart(id):
    auth0_id = request.jwt_payload['sub']
    query = select(User).where(User.auth0_id == auth0_id)
    user = db.session.execute(query).scalars().first()
    if not user:
        return jsonify({"status": "error","message":"User not found"}), 404
    
    cart = db.session.get(Cart, id)
    if not cart:
        return jsonify({"status": "error","message":"Cart not found"}), 404
    db.session.delete(cart)
    db.session.commit()   
    return jsonify({"status": "success","message":"Successfully deleted!"}), 200

# Payment Method
@cart_bp.route("/create-payment-intent", methods=["POST"])
@token_required
def create_payment():
    try:
        data = request.json
        intent = stripe.PaymentIntent.create(
            amount=data['price'],  # $50.00 in cents
            currency=data['currency'],
            automatic_payment_methods={"enabled": True},
        )
        return jsonify({"clientSecret": intent.client_secret, "paymentIntentId": intent.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@cart_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': data['priceId'],
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:5173/success' +
            '?success=true&session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5173/cancel' + '?canceled=true',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return "Server error", 500
   