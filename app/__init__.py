from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.users import users_bp
from app.blueprints.addresses import addresses_bp
from app.blueprints.categories import categories_bp
from app.blueprints.products import products_bp
from app.blueprints.product_images import product_images_bp
from app.blueprints.product_variants import product_variants_bp
from app.blueprints.reviews import reviews_bp
from app.blueprints.cart import cart_bp
from app.blueprints.cart_item import cart_item_bp
from app.blueprints.product_images import product_images_bp
from app.blueprints.orders import orders_bp
from app.blueprints.order_items import order_items_bp
from app.blueprints.payments import payments_bp
from app.blueprints.discounts import discounts_bp
from app.blueprints.shipping import shipping_details_bp
from app.blueprints.wishlists import wishlists_bp


from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs' 
API_URL = '/static/swagger.yaml'

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Marketplace MAnagement API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(addresses_bp, url_prefix='/addresses')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(product_images_bp, url_prefix='/product_images')
    app.register_blueprint(product_variants_bp, url_prefix='/product_variants')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(cart_bp, url_prefix='/carts')
    app.register_blueprint(cart_item_bp, url_prefix='/cart_items')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(order_items_bp, url_prefix='/order_items')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(discounts_bp, url_prefix='/discounts')
    app.register_blueprint(shipping_details_bp, url_prefix='/shipping')
    app.register_blueprint(wishlists_bp, url_prefix='/wishlists')

    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    return app
