from flask import Blueprint

product_images_bp = Blueprint('product_images_bp',__name__)

from . import routes