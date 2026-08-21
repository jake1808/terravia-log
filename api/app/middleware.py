import jwt
from functools import wraps
from flask import  request, jsonify, current_app
from app.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token= None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"error": "Token is missing! Log in first"}), 401
        
        try:
            # Decode the token to get the User ID
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token has expired! Please log in again."}), 401
        except Exception as e:
            return jsonify({"error": "Token is invalid!"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated