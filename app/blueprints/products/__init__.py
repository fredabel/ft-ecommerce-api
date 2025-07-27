from flask import Blueprint

products_bp = Blueprint('products_bp',__name__)

from . import routes