from flask import Blueprint

cart_item_bp = Blueprint('cart_item_bp',__name__)

from . import routes