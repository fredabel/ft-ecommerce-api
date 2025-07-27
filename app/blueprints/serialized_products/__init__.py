from flask import Blueprint

serialized_products_bp = Blueprint('serialized_products_bp',__name__)

from . import routes