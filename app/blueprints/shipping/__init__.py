from flask import Blueprint

shipping_details_bp = Blueprint('shipping_details_bp',__name__)

from . import routes