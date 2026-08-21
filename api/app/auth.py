import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({"error": "Name, email, password and role are required"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Database error"}), 400
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(name=data['name'], email=data['email'], password_hash=hashed_password, role=data['role'])
    db.session.add(new_user)
    
    try:
        db.session.commit()
        return jsonify({"message":"User registered successfully!", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":"Database error"}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout(current_user):
    # Because JWT is stateless, the server doesn't need to "do" anything to log the user out.
    # The client is responsible for deleting the token from their local storage/app.
    return jsonify({"message": "Successfully logged out."}), 200
    
    