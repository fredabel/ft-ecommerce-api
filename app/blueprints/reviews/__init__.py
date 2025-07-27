from flask import Blueprint

reviews_bp = Blueprint('reviews_bp',__name__)

from . import routes