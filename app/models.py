from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime, timezone
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True)
    auth0_id: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=True)
    image_url: Mapped[str] = mapped_column(db.String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(db.String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(db.String(100), nullable=True)
    email: Mapped[str] = mapped_column(db.String(100),unique=False, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=True)
    billing_address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    shipping_address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_user: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    cart: Mapped["Cart"] = db.relationship(back_populates="user")
    wishlist: Mapped["WishList"] = db.relationship(back_populates="user")
    orders: Mapped[List["Order"]] = db.relationship(back_populates="user")
    addresses: Mapped[List["Address"]] = db.relationship(back_populates="user")
    reviews: Mapped[List["Review"]] = db.relationship("Review", back_populates="user")
    
class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    address_line1: Mapped[str] = mapped_column(db.String(255), nullable=False)
    address_line2: Mapped[str] = mapped_column(db.String(255), nullable=True)
    city: Mapped[str] = mapped_column(db.String(100), nullable=False)
    state: Mapped[str] = mapped_column(db.String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(db.String(20), nullable=False)
    country: Mapped[str] = mapped_column(db.String(100), nullable=False)
    address_type: Mapped[str] = mapped_column(db.String(50), default="billing", nullable=False)  # e.g., 'billing', 'shipping'
    is_default: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = db.relationship(back_populates="addresses")


class Category(db.Model):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    image: Mapped[str] = mapped_column(db.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    products: Mapped[List["Product"]] = db.relationship(back_populates="category")
    
class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), nullable=False)
    brand: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    image_url: Mapped[str] = mapped_column(db.String(255), nullable=True)
    weight: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=True)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    category: Mapped["Category"] = db.relationship(back_populates="products")
    cart_items: Mapped[List["CartItem"]] = db.relationship("CartItem", back_populates="product")
    variants: Mapped[List["ProductVariant"]] = db.relationship("ProductVariant", back_populates="product")
    order_items: Mapped[List["OrderItem"]] = db.relationship("OrderItem", back_populates="product")
    images: Mapped[List["ProductImage"]] = db.relationship("ProductImage", back_populates="product")
    wishlists: Mapped[List["WishList"]] = db.relationship("WishList", back_populates="product")
    reviews: Mapped[List["Review"]] = db.relationship("Review", back_populates="product")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    size: Mapped[str] = mapped_column(db.String(50), nullable=True)
    color: Mapped[str] = mapped_column(db.String(50), nullable=True)
    sku: Mapped[str] = mapped_column(db.String(100), nullable=True)
    price_modifier: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=True)
    stock: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_discounted: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    discount_percentage: Mapped[float] = mapped_column(db.Numeric(5, 2), nullable=True)
    discount_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=True)
    discount_start_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    discount_end_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    is_new: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_popular: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    is_on_sale: Mapped[bool] = mapped_column(db.Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    product: Mapped["Product"] = db.relationship(back_populates="variants")
    order_items: Mapped[List["OrderItem"]] = db.relationship("OrderItem", back_populates="variant")
    cart_items: Mapped[List["CartItem"]] = db.relationship("CartItem", back_populates="variant")

class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    img_url: Mapped[str] = mapped_column(db.String(255), nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(db.String(50), nullable=True)
    alt_text: Mapped[str] = mapped_column(db.String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    product: Mapped["Product"] = db.relationship(back_populates="images")
    
class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    cart_id: Mapped[int] = mapped_column(db.ForeignKey("carts.id"), nullable=True)
    order_number: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    subtotal_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    shipping_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False, default=0.0)
    total_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    shipping_address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    billing_address: Mapped[str] = mapped_column(db.String(255), nullable=True)
    discount_id: Mapped[int] = mapped_column(db.ForeignKey("discounts.id"), nullable=True)
    order_status: Mapped[str] = mapped_column(db.String(50), nullable=False, default="pending")
    order_date: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = db.relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = db.relationship("OrderItem", back_populates="order")
    payments: Mapped[List["Payment"]] = db.relationship("Payment", back_populates="order")
    shipping_info: Mapped["ShippingDetails"] = db.relationship("ShippingDetails", back_populates="order")
    discount: Mapped["Discount"] = db.relationship("Discount", back_populates="orders")
    cart: Mapped["Cart"] = db.relationship("Cart", back_populates="orders", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(db.ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(db.ForeignKey("product_variants.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    order: Mapped["Order"] = db.relationship(back_populates="order_items")
    product: Mapped["Product"] = db.relationship(back_populates="order_items")
    variant: Mapped["ProductVariant"] = db.relationship("ProductVariant", back_populates="order_items")
    
class Cart(Base):
    __tablename__ = "carts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=True)
    session_id: Mapped[str] = mapped_column(db.String(255), nullable=True, unique=True)  # For guest carts
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = db.relationship(back_populates="cart")
    cart_items: Mapped[List["CartItem"]] = db.relationship("CartItem", back_populates="cart", cascade="all, delete")
    orders: Mapped[List["Order"]] = db.relationship("Order", back_populates="cart", uselist=False)
    
class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(db.ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(db.ForeignKey("product_variants.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(db.Integer, default=1, nullable=False)
    added_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    cart: Mapped["Cart"] = db.relationship("Cart", back_populates="cart_items")
    product: Mapped["Product"] = db.relationship("Product", back_populates="cart_items")
    variant: Mapped["ProductVariant"] = db.relationship("ProductVariant", back_populates="cart_items")
   
class Payment(Base):
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(db.ForeignKey("orders.id"), nullable=False)
    payment_intent_id: Mapped[int] = mapped_column(db.String(255), nullable=False)
    payment_method: Mapped[str] = mapped_column(db.String(20), nullable=False)
    transaction_id: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(db.String(10), nullable=False)
    payment_status: Mapped[str] = mapped_column(db.String(20), nullable=False, default="pending") # e.g., 'pending', 'completed', 'failed'
    payment_date: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    refunded_amount: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    order: Mapped["Order"] = db.relationship("Order", back_populates="payments")

class ShippingDetails(Base):
    __tablename__ = "shipping_details"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(db.ForeignKey("orders.id"), nullable=False)
    shipping_method: Mapped[str] = mapped_column(db.String(50), nullable=False)
    shipping_cost: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    tracking_number: Mapped[str] = mapped_column(db.String(100), nullable=True)
    shipping_status: Mapped[str] = mapped_column(db.String(50), nullable=False, default="pending")  # e.g., 'pending', 'shipped', 'delivered'
    estimated_delivery: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    order: Mapped["Order"] = db.relationship("Order", back_populates="shipping_info")
    
class Discount(Base):
    __tablename__ = "discounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    discount_type: Mapped[str] = mapped_column(db.String(20), nullable=False)  # e.g., 'percentage', 'fixed'
    discount_value: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    start_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    orders: Mapped[List["Order"]] = db.relationship("Order", back_populates="discount")

class WishList(Base):
    __tablename__ = "wishlists"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user: Mapped["User"] = db.relationship(back_populates="wishlist")
    product: Mapped["Product"] = db.relationship(back_populates="wishlists")

class Review(Base):
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("products.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(db.Integer, nullable=False)  # e.g., 1 to 5 stars
    comment: Mapped[str] = mapped_column(db.String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    product: Mapped["Product"] = db.relationship("Product", back_populates="reviews")
    user: Mapped["User"] = db.relationship("User", back_populates="reviews")
