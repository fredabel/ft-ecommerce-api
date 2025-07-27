from flask import request, jsonify
from app.blueprints.wishlists import wishlists_bp
from app.blueprints.wishlists.schemas import wishlist_schema, wishlists_schema
from marshmallow import ValidationError
from app.models import WishList, User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required



@wishlists_bp.route("/", methods=['POST'])
@token_required
def create_wishlist():
    try:
        auth0_id = request.jwt_payload['sub']
        qry = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(qry).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found"}), 404
        # wishlist_data = wishlist_schema.load(request.json)
        new_wishlist = WishList(
            user_id=user.id,
            product_id=request.json.get('product_id')
        )
        db.session.add(new_wishlist)
        db.session.commit()
        return wishlist_schema.jsonify(new_wishlist), 201
    except ValidationError as err:
        return jsonify(err.messages), 400