from flask import request, jsonify
from app.blueprints.product_variants import product_variants_bp
from app.blueprints.product_variants.schemas import product_variant_schema, product_variants_schema
from marshmallow import ValidationError
from app.models import ProductVariant, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@product_variants_bp.route('/', methods=['POST'])
def create_product_variant():
    try:
        variant_data = product_variant_schema.load(request.json)
        new_variant = ProductVariant(
            product_id=variant_data['product_id'],
            price_modifier=variant_data['price_modifier'],
            size=variant_data.get('size', ''),
            color=variant_data.get('color', ''),
            sku=variant_data.get('sku', ''),
            stock=variant_data.get('stock', 0),
            is_default=variant_data.get('is_default', False),
            is_on_sale=variant_data.get('is_on_sale', False),
            is_featured=variant_data.get('is_featured', False),
            is_new=variant_data.get('is_new', False),
            is_discounted=variant_data.get('is_discounted', False),
            discount_amount=variant_data.get('discount_amount', 0.0),
            discount_percentage=variant_data.get('discount_percentage', 0.0),
            is_active=variant_data.get('is_active', True)
        )
        db.session.add(new_variant)
        db.session.commit()
        return jsonify({"status": "success", "message": "Product variant created successfully", "variant": product_variant_schema.dump(new_variant)}), 201
    except ValidationError as e:
        return jsonify({"status": "error", "message": "Invalid product variant data", "errors": e.messages}), 400

@product_variants_bp.route('/<int:id>', methods=['GET'])
def get_product_variant(id):
    try:
        variant = db.session.execute(select(ProductVariant).where(ProductVariant.id == id)).scalar()
        if not variant:
            return jsonify({"status": "error", "message": "Product variant not found"}), 404
        return jsonify({"status": "success", "variant": product_variant_schema.dump(variant)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to retrieve product variant", "errors": str(e)}), 500