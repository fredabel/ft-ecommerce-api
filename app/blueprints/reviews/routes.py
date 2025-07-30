from flask import request, jsonify
from app.blueprints.reviews import reviews_bp
from app.blueprints.reviews.schemas import review_schema, reviews_schema
from marshmallow import ValidationError
from app.models import Review, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required

@reviews_bp.route("/", methods=['POST'])
@token_required
def create_review():
    try:
        auth0_id = request.jwt_payload['sub']
        qry = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(qry).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404
        review_data = review_schema.load(request.json)
        new_review = Review(
            user_id=user.id,
            product_id=review_data['product_id'],
            rating=review_data['rating'],
            comment=review_data.get('comment', ''),
        )
        db.session.add(new_review)
        db.session.commit()
        return review_schema.jsonify(new_review), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

    
@reviews_bp.route("/", methods=['GET'])
def get_product_reviews():
    try:
        product_id = request.args.get('product_id', type=int)
        qry = select(Review).where(Review.product_id == product_id)
        reviews = db.session.execute(qry).scalars().all()
        return jsonify(reviews_schema.dump(reviews)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@reviews_bp.route("/my_reviews", methods=['GET'])
@token_required
def get_my_reviews():
    try:
        auth0_id = request.jwt_payload['sub']
        qry = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(qry).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        stmt = select(Review).where(Review.user_id == user.id)
        reviews = db.session.execute(stmt).scalars().all()
        return jsonify(reviews_schema.dump(reviews)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
