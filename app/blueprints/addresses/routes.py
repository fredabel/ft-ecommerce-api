from flask import request, jsonify
from app.blueprints.addresses import addresses_bp
from app.blueprints.addresses.schemas import address_schema, addresses_schema
from marshmallow import ValidationError
from app.models import Address, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@addresses_bp.route('/', methods=['POST'])
@token_required
def create_address():
    try:
        address_data = address_schema.load(request.json)
        new_address = Address(
            user_id=address_data['user_id'],
            address_line1=address_data['address_line1'],
            address_line2=address_data['address_line2'],
            city=address_data['city'],
            state=address_data['state'],
            zip_code=address_data['zip_code'],
            country=address_data['country'],
            # address_type=address_data['address_type']
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({"status": "success", "message": "Address created successfully", "address": address_schema.dump(new_address)}), 201
    except ValidationError as e:
        return jsonify({"status": "error", "message": "Invalid address data", "errors": e.messages}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to create address", "errors": str(e)}), 500