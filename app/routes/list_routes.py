# app/routes/list_routes.py
from flask import Blueprint, request, jsonify
from app.list_management_service import ListManagementService

bp = Blueprint('list_routes', __name__)
service = ListManagementService()

@bp.route('/list/<int:list_id>/check', methods=['POST'])
def check_value(list_id):
    data = request.json
    result = service.check_value(list_id, data['value'])
    return jsonify(result)
