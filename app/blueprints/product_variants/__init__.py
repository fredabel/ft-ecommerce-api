from flask import Blueprint

product_variants_bp = Blueprint('product_variants_bp',__name__)

from . import routes