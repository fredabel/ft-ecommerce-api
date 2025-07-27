from flask import Blueprint

order_items_bp = Blueprint('order_items_bp',__name__)

from . import routes