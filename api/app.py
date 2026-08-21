import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-dev-key')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    
    def to_dict(self):
        return{"id":self.id, "name":self.name, "email":self.email, 'role':self.role}

# --- MIDDLEWARE: TOKEN REQUIRED ---
# This ensures a valid JWT for specific routes
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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token has expired! Please log in again."}), 401
        except Exception as e:
            return jsonify({"error": "Token is invalid!"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# --- AUTHENTICATION ROUTES ---
@app.route('/register', methods=['POST'])
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

@app.route('/login', methods=['POST'])
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
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": user.to_dict()
    }), 200

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # Because JWT is stateless, the server doesn't need to "do" anything to log the user out.
    # The client is responsible for deleting the token from their local storage/app.
    return jsonify({"message": "Successfully logged out."}), 200

# --- Protected route ---
@app.route('/', methods=['GET'])
@token_required
def home(current_user):
    return jsonify({"message":"You have accessed a protected route!", "user": current_user.to_dict()}), 200

with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG'))