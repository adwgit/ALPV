# app/routes/report_routes.py
from flask import Blueprint, jsonify
from app.list_management_service import ListManagementService

bp = Blueprint('report_routes', __name__)
service = ListManagementService()

@bp.route('/report/actions', methods=['GET'])
def get_action_report():
    result = service.get_action_report('admin')
    return jsonify(result)
