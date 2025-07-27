from flask import request, jsonify
from app.blueprints.product_images import product_images_bp
from app.blueprints.product_images.schemas import product_image_schema, product_images_schema
from marshmallow import ValidationError
from app.models import ProductImage, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import encode_token, token_required


@product_images_bp.route('/', methods=['POST'])
def create_product_image():
    try:
        image_data = product_image_schema.load(request.json)
        new_image = ProductImage(
            product_id=image_data['product_id'],
            img_url=image_data['img_url'],
            alt_text=image_data.get('alt_text', ''),
            thumbnail_url=image_data.get('thumbnail_url', ''),
            is_primary=image_data.get('is_primary', False) 
        )
        db.session.add(new_image)
        db.session.commit()
        return jsonify({"status": "success", "message": "Product image created successfully", "image": product_image_schema.dump(new_image)}), 201
    except ValidationError as e:
        return jsonify({"status": "error", "message": "Invalid product image data", "errors": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to create product image", "errors": str(e)}), 500