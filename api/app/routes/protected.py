from flask import Blueprint, request, jsonify
from app.middleware import token_required

protected_bp = Blueprint('protected', __name__)

@protected_bp.route('/', methods=['GET'])
@token_required
def home(current_user):
    return jsonify({"message":"You have accessed a protected route!", "user": current_user.to_dict()}), 200 