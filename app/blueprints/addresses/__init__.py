from flask import Blueprint

addresses_bp = Blueprint('addresses_bp',__name__)

from . import routes