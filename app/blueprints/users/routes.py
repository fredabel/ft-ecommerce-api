from flask import request, jsonify
from app.blueprints.users import users_bp
from app.blueprints.users.schemas import user_schema, users_schema, login_schema
from marshmallow import ValidationError
from app.models import User, db
from sqlalchemy import select, delete
from app.extensions import limiter
from app.extensions import cache
from app.utils.util import  token_required
from werkzeug.security import generate_password_hash, check_password_hash

@users_bp.route("/sync", methods=['POST'])
def get_or_create_user():
    try:
        user_data = user_schema.load(request.json)
        user = db.session.query(User).filter(User.auth0_id==user_data['auth0_id']).first()
        if not user:
            user = User(
                email = user_data['email'],
                full_name = user_data['full_name'],
                image_url = user_data['image_url'],
                auth0_id = user_data['auth0_id']
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({"status":"success","message":"Successfully created user","user": user_schema.dump(user)}), 201
        else:
            return jsonify({"status":"success","message":"User already exist","user": user_schema.dump(user)}), 200
        
    except ValidationError as err:
        return jsonify(err.messages), 400

# -------------------- Get All users --------------------
# This route retrieves all users.
# Cached for 30 seconds to improve performance.
# Rate limited to 10 requests per hour to prevent abuse.
@users_bp.route("/",methods=['GET'])
# @cache.cached(timeout=30)
# @limiter.limit("10/hour")
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if page < 1 or per_page < 1:
        return jsonify({"status": "error", "message": "Page and per_page must be greater than 0."}), 400
    query = select(User)
    pagination = db.paginate(query, page=page, per_page=per_page)
    return jsonify({
        "users": users_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages
    }), 200
    
@users_bp.route("/me",methods=['GET'])
@token_required
def profile():
    auth0_id = request.jwt_payload['sub']
    query = select(User).where(User.auth0_id == auth0_id)
    user = db.session.execute(query).scalars().first()
    if user == None:
        return jsonify({"status":"error","message":"Invalid user"}), 404
    return jsonify({"status":"success","message":"Successfuly fetch user","user": user_schema.dump(user)}), 200
# -------------------- Get a Specific user --------------------
# This route retrieves a specific user by their ID.
# Cached for 30 seconds to reduce database lookups.
@users_bp.route("/<int:user_id>",methods=['GET'])
@limiter.exempt
# @cache.cached(timeout=30)
def get_user(user_id):
    query = select(User).where(User.id == user_id)
    user = db.session.execute(query).scalars().first()
    if user == None:
        return jsonify({"status":"error","message":"Invalid user"}), 404
    return user_schema.jsonify(user), 200

# -------------------- Update a user --------------------
# This route allows updating a user's details by their ID.
# Validates the input and ensures the email is unique.
# Rate limited to 5 requests per hour to prevent abuse.
@users_bp.route("/", methods=['PUT'])
# @limiter.limit("5/hour")
@token_required
def update_user():
    auth0_id = request.jwt_payload['sub']
    query = select(User).where(User.auth0_id == auth0_id)
    user = db.session.execute(query).scalars().first()
    if user == None:
        return jsonify({"status":"error","message":"Invalid user"}), 404
    
    try:
        user_data = user_schema.load(request.json)
        if request.args.get('password'):
            user_data['password'] = generate_password_hash(user_data['password'])
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if user_data['email'] != user.email:
        email_exist = db.session.execute(select(User).where(User.email == user_data['email'])).scalar_one_or_none()
        if email_exist:
            return jsonify({"status":"error", "message": "A user with this email already exists"}), 400
    
    user_data['full_name'] = f"{user_data['first_name']} {user_data['last_name']}".title()    
    
    for field, value in user_data.items():
        setattr(user, field, value)
    db.session.commit()
    return jsonify({"status":"success","message":"Successfully updated user","user": user_schema.dump(user)}), 200

# -------------------- Delete a user --------------------
# This route allows deleting a user by their ID.
# Rate limited to 5 requests per day to prevent abuse.
# Requires a valid token for authentication.
@users_bp.route("/", methods=['DELETE'])
# @limiter.limit("5/day")
@token_required
def delete_user():
    query = select(User).where(User.id == request.userid)
    user = db.session.execute(query).scalars().first()
    if user == None:
        return jsonify({"status":"error","message":"Invalid user"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status":"success","message": f"Succesfully deleted user {request.userid}"}), 200

# -------------------- Search user --------------------
# This route allows searching for mechanics by their name.
# Cached for 30 seconds to improve performance.
@users_bp.route("/search", methods=['GET'])
# @cache.cached(timeout=30)
def search_user():
    
    name = request.args.get('name')
    email = request.args.get('email')
    
    #For future updates, pagination can be added
    # page = request.args.get('page', default=1, type=int)
    # per_page = request.args.get('per_page', default=10, type=int)
    
    if not name and not email:
        return jsonify({"status":"error","message": "At least one search parameter (name or email) is required."}), 400

    query = select(User)
    filters = []
    if name:
        filters.append(User.name.ilike(f'%{name}%'))
    if email:
        filters.append(User.email.ilike(f'%{email}%'))
    if filters:
        query = query.where(*filters)
        
    # users = db.paginate(query, page=page, per_page=per_page)
    users = db.session.execute(query).scalars().all()
    # if not users:
    #     return jsonify({"status": "error","message": "No users found"}), 404
    return users_schema.jsonify(users), 200
