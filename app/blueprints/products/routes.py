from flask import request, jsonify
from app.blueprints.products import products_bp
from app.blueprints.products.schemas import product_schema, products_schema
from marshmallow import ValidationError
from app.models import Product, db
from sqlalchemy import select, delete
from app.extensions import cache, limiter
# from app.utils.util import token_required

# -------------------- Create a product --------------------
# This route allows the creation of a new product.
# Rate limited to 10 requests per hour to prevent spamming.
@products_bp.route("/",methods=['POST'])
# @limiter.limit("10/hour")
def create_product():
    try:
        product_data = product_schema.load(request.json)
        new_product = Product(**product_data)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"status": "success","message":"Successfully created product","product": product_schema.dump(new_product)}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    

# -------------------- Get All products --------------------
# This route retrieves all products.
# Cached for 30 seconds to improve performance.
# Rate limited to 10 requests per minute to prevent excessive requests.
@products_bp.route("/",methods=['GET'])
# @cache.cached(timeout=30)
# @limiter.limit("10/hour")
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = select(Product)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "items": products_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200
    

# -------------------- Get a Specific products --------------------
# This route retrieves a specific product by their ID.
# Cached for 30 seconds to reduce database lookups.
@products_bp.route("/<int:product_id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_product(product_id):
    query = select(Product).where(Product.id == product_id)
    product = db.session.execute(query).scalars().first()
    if product == None:
        return jsonify({"status":"error","message":"Invalid product"}), 404
    return product_schema.jsonify(product), 200

# -------------------- Update a product --------------------
# This route allows updating a product by its ID.
# Rate limited to 10 requests per hour.
@products_bp.route("/<int:product_id>", methods=['PUT'])
# @limiter.limit("10/hour")
def update_product(product_id):
    try:
        product_data = product_schema.load(request.json)
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"status": "error","message":"Product not found"}), 404
        
        for field, value in product_data.items():
            setattr(product, field, value)
        
        db.session.commit()
        return jsonify({"status": "success","message":"Successfully updated product","product": product_schema.dump(product)}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

# -------------------- Delete a product --------------------
# This route allows deleting a product by its ID.
# Rate limited to 5 requests per day to prevent abuse. 
@products_bp.route("/<int:product_id>", methods=['DELETE'])
# @limiter.limit("5/day")
def delete_product(product_id):
    
    product = db.session.get(Product, product_id)
    
    if not product:
        return jsonify({"status": "error","message":"Product not found"}), 404
    
    # Check for related serialized parts
    if product.serial_products:
        return jsonify({"status": "error", "message": "Cannot delete: related serialized product exist."}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"status": "success","message": "Successfully deleted product"}), 200

# -------------------- Search products --------------------
# This route allows searching for products by name.
# Rate limited to 15 requests per minute.
@products_bp.route("/search", methods=['GET'])
# @limiter.limit("15/minute")
def search_products():
    name = request.args.get('name')
    brand = request.args.get('brand')
    if not name and not brand:
        return jsonify({"status":"error","message": "Please provide a name or brand to search"}), 400
    query = select(Product)
    filters = []
    if name:
        filters.append(Product.name.ilike(f"%{name}%"))
    if brand:
        filters.append(Product.brand.ilike(f"%{brand}%"))
    if filters:
        query = query.where(*filters)
        
    products = db.session.execute(query).scalars().all()
    return products_schema.jsonify(products), 200