from flask import Blueprint

discounts_bp = Blueprint('discounts_bp',__name__)

from . import routes