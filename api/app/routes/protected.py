from flask import Blueprint, request, jsonify
from app.middleware import token_required
from app.models import User, Pilot, Drone, db

protected_bp = Blueprint('protected', __name__)

@protected_bp.route('/', methods=['GET'])
@token_required
def home(current_user):
    return jsonify({"message":"You have accessed a protected route!", "user": current_user.to_dict()}), 200 

@protected_bp.route('/admin', methods=['GET'])
@token_required
def admin(current_user):
    if current_user.role != 'admin':
        return jsonify({"message":"You do not have permission to access this route."}), 403
    pilot = db.session.query(Pilot).filter_by(is_active=True)
    drone = db.session.query(Drone).filter_by(is_active=True)
    return jsonify({"message":"Welcome to the admin route!", "user": current_user.to_dict(), "pilots": [p.to_dict() for p in pilot], "drones": [d.to_dict() for d in drone]}), 200