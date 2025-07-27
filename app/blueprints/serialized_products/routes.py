from flask import request, jsonify
from app.blueprints.serialized_products import serialized_products_bp
from app.blueprints.serialized_products.schemas import serialized_product_schema, serialized_products_schema
from app.blueprints.products.schemas import product_schema
from marshmallow import ValidationError
from app.models import SerializedProduct, Product, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
# from app.utils.util import role_required

# -------------------- Create a Serialized Part --------------------
# This route allows the creation of a new serialized part.
# Rate limited to 10 requests per hour to prevent spamming.
@serialized_products_bp.route("/",methods=['POST'])
@limiter.limit("10/minute")
def create_serialized_product():
    try:
        serialized_product_data = serialized_product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product = db.session.get(Product, serialized_product_data['product_id'])
    
    if not product:
        return jsonify({"status": "error","message":"product description not found"}), 404
    
    new_serialized_product = SerializedProduct(**serialized_product_data)
    db.session.add(new_serialized_product)
    db.session.commit()
    
    data = serialized_product_schema.dump(new_serialized_product)
    data["message"] = "Successfully created serialized product"
    data["status"] = "success"
    return jsonify(data), 201

# -------------------- Get All Serialized Parts --------------------
# This route retrieves all serialized parts.
# Cached for 60 seconds to improve performance.
@serialized_products_bp.route("/",methods=['GET'])
# @cache.cached(timeout=60)
def get_serialized_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = select(SerializedProduct)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "items": serialized_products_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200  

# -------------------- Get a Specific Serialized Part --------------------
# This route retrieves a specific serialized part by their ID.
# Cached for 30 seconds to reduce database lookups.
@serialized_products_bp.route("/<int:id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_mechanic(id):
    query = select(SerializedProduct).where(SerializedProduct.id == id)
    serialized_product = db.session.execute(query).scalars().first()
    if serialized_product == None:
        return jsonify({"message":"Invalid serialized product"}), 404
    return serialized_product_schema.jsonify(serialized_product), 200

# -------------------- Search Serialized Parts --------------------
# This route allows searching for serialized parts by name.
# Rate limited to 15 requests per minute.
# @serialized_products_bp.route("/search", methods=['GET'])
# @limiter.limit("15/minute")
# def search_serialized_products():
#     name = request.args.get('name')
#     query = select(SerializedProduct).where(SerializedProduct.name.like(f'%{name}%'))
#     serialized_products = db.session.execute(query).scalars().all()
#     return serialized_products_schema.jsonify(serialized_products), 200

# -------------------- Update a Serialized Part --------------------
# This route allows updating a serialized part by its ID.
# Rate limited to 10 requests per hour.
@serialized_products_bp.route("/<int:id>", methods=['PUT'])
@limiter.limit("10/hour")
def update_serialized_product(id):
    
    try:
        serialized_product_data = serialized_product_schema.load(request.json)

    except ValidationError as err:
        return jsonify(err.messages), 400
    
    serialized_product = db.session.get(SerializedProduct, id)
    if not serialized_product:
        return jsonify({"status": "error","message":"Serialized part not found"}), 404
    
    product = db.session.get(Product, serialized_product_data['product_id'])
    if not product:
        return jsonify({"status": "error","message":"Product not found"}), 404

    for field, value in serialized_product_data.items():
        setattr(serialized_product, field, value)
    
    db.session.commit()
    
    data = serialized_product_schema.dump(serialized_product)
    data["message"] = "Successfully updated serialized product"
    data["status"] = "success"
    return jsonify(data), 200

# -------------------- Delete a Serialized Part --------------------
# This route allows deleting a serialized part by its ID.
# Rate limited to 5 requests per day.
@serialized_products_bp.route("/<int:id>", methods=['DELETE'])
@limiter.limit("5/day")
def delete_serialized_product(id):
    serialized_product = db.session.get(SerializedProduct, id)
    if not serialized_product:
        return jsonify({"status": "error","message":"Serialized product not found"}), 404
    
    db.session.delete(serialized_product)
    db.session.commit()
    return jsonify({"status": "success","message": f"Successfully deleted serialized product {id}"}), 200



    
    
