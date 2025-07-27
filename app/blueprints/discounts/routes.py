from flask import request, jsonify
from app.blueprints.discounts import discounts_bp
from app.blueprints.discounts.schemas import discount_schema, discounts_schema
from marshmallow import ValidationError
from app.models import Discount, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required
from datetime import datetime

@discounts_bp.route("/", methods=['POST'])
def create_discount():
    try:
        # Parse dates from string to datetime objects
        start_date_str = request.json.get('start_date', '2025-05-01 00:00:00')
        end_date_str = request.json.get('end_date', '2025-12-31 23:59:59')
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
        
        # Assuming discount data is sent in the request body
        new_discount = Discount(
            code=request.json.get('code'),
            discount_type=request.json.get('discount_type', 'percentage'),
            discount_value=request.json.get('value', 0.0),
            start_date=start_date,
            end_date=end_date,
            is_active=request.json.get('active', True)
        )
        db.session.add(new_discount)
        db.session.commit()
        return jsonify({"status": "success", "message": "Discount created successfully", "discount": discount_schema.dump(new_discount)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400