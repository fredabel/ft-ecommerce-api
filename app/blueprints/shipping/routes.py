from flask import request, jsonify
from app.blueprints.shipping import shipping_details_bp
from app.blueprints.shipping.schemas import shipping_detail_schema, shipping_details_schema
from marshmallow import ValidationError
from app.models import ShippingDetails, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@shipping_details_bp.route("/", methods=['POST'])
def create_shipping_details():
    try:
        shipping_details = shipping_detail_schema.load(request.json)
        new_shipping_details = ShippingDetails(**shipping_details)
        db.session.add(new_shipping_details)
        db.session.commit()
        return shipping_detail_schema.jsonify(new_shipping_details), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
