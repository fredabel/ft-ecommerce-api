from flask import request, jsonify
from app.blueprints.addresses import addresses_bp
from app.blueprints.addresses.schemas import address_schema, addresses_schema
from marshmallow import ValidationError
from app.models import Address, User, db
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

@addresses_bp.route('/my_address', methods=['GET'])
@token_required
def get_my_address():
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        query = select(Address).where(Address.user_id == user.id)
        addresses = db.session.execute(query).scalars().all()
        if addresses == None:
            return jsonify({"status":"error","message":"Invalid addresses"}), 404
        
        return jsonify(addresses_schema.dump(addresses)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get address", "errors": str(e)}), 500
    
    
@addresses_bp.route('/my_address/<int:id>', methods=['PUT'])
@token_required
def update_my_address(id):
    try:
        address_data = address_schema.load(request.json)
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        query = select(Address).where(Address.user_id == user.id, Address.id == id)
        address = db.session.execute(query).scalars().first()
        
        if address == None:
            return jsonify({"status":"error","message":"Invalid addresses"}), 404
        
        for field, value in address_data.items():
            setattr(address, field, value)
        return jsonify(address_schema.dump(address)), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get address", "errors": str(e)}), 500

    
@addresses_bp.route('/my_address/<int:id>', methods=['DELETE'])
@token_required
def deelte_my_address(id):
    try:
        auth0_id = request.jwt_payload['sub']
        query = select(User).where(User.auth0_id == auth0_id)
        user = db.session.execute(query).scalars().first()
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        address = db.session.get(Address,id)
        
        if address == None:
            return jsonify({"status":"error","message":"Invalid addresses"}), 404
        
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({"status": "success","message": "Successfully deleted address"}), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to get address", "errors": str(e)}), 500