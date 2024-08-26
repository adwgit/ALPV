# app/routes/user_routes.py
from flask import Blueprint, request, jsonify
from app.list_management_service import ListManagementService

bp = Blueprint('user_routes', __name__)
service = ListManagementService()

@bp.route('/user/create', methods=['POST'])
def create_user():
    data = request.json
    result = service.create_user(data['username'], data['password'], data['role'])
    return jsonify(result)
