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
            discount_value=request.json.get('discount_value',0),
            start_date=start_date,
            end_date=end_date,
            is_active=request.json.get('active', True)
        )
        db.session.add(new_discount)
        db.session.commit()
        return jsonify({"status": "success", "message": "Discount created successfully", "discount": discount_schema.dump(new_discount)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@discounts_bp.route("/get_code",methods=['GET'])
def get_discount_by_code():
    try:
        code=request.args.get('code')
        if not code:
            return jsonify({"status": "error", "message": "No code provided"}), 400
       
        discount = db.session.execute(select(Discount).where(Discount.code == code )).scalars().first()
        
        if not discount:
            return jsonify({"status": "error", "message": "Discount not found"}), 404
        return jsonify(discount_schema.dump(discount)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to fetch discount", "errors": str(e)}), 500

@discounts_bp.route("/<int:id>",methods=['GET'])
def get_discount(id):
    try:
        discount = db.session.get(Discount, id)
        if not discount:
            return jsonify({"status": "error", "message": "Discount not found"}), 404
        return jsonify(discount_schema.dump(discount)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to fetch discount", "errors": str(e)}), 500
        

@discounts_bp.route("/<int:id>", methods=['PUT'])
def update_discount(id):
    try:
        discount = db.session.get(Discount, id)
        if not discount:
            return jsonify({"status": "error", "message": "Discount not found"}), 404

        payload = request.json

        # Handle date fields if present
        if 'start_date' in payload:
            discount.start_date = datetime.strptime(payload['start_date'], "%Y-%m-%d %H:%M:%S")
        if 'end_date' in payload:
            discount.end_date = datetime.strptime(payload['end_date'], "%Y-%m-%d %H:%M:%S")

        # Update other fields
        for field in ['code', 'discount_type', 'discount_value', 'is_active']:
            if field in payload:
                setattr(discount, field, payload[field])

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Discount updated successfully",
            "discount": discount_schema.dump(discount)
        }), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to update discount", "errors": str(e)}), 500

@discounts_bp.route("/<int:id>", methods=['DELETE'])
def delete_discount(id):
    try:
        discount = db.session.get(Discount, id)
        if not discount:
            return jsonify({"status": "error", "message": "Discount not found"}), 404

        db.session.delete(discount)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Discount deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to delete discount", "errors": str(e)}), 500