from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.api.leave.schemas import (
    LeaveRequestCreateSchema,
    LeaveReviewSchema,
    LeaveRequestResponseSchema,
)
from app.services import leave_service
from app.utils.decorators import role_required
from app.models import Employee
from datetime import datetime

leave_bp = Blueprint("leave", __name__)

create_schema = LeaveRequestCreateSchema()
review_schema = LeaveReviewSchema()
response_schema = LeaveRequestResponseSchema()
response_list_schema = LeaveRequestResponseSchema(many=True)


@leave_bp.post("")
@jwt_required()
def apply_for_leave():
    try:
        data = create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user_id = get_jwt_identity()
    leave_request = leave_service.create_leave_request(user_id, data)
    if not leave_request:
        return jsonify({"message": "Failed to create leave request"}), 400

    return jsonify(response_schema.dump(leave_request)), 201


@leave_bp.get("/my")
@jwt_required()
def my_leave_requests():
    user_id = get_jwt_identity()
    requests_ = leave_service.get_requests_for_user(user_id)
    return jsonify(response_list_schema.dump(requests_)), 200


@leave_bp.get("/pending")
@role_required("admin", "hr_manager")
def pending_requests():
    requests_ = leave_service.get_pending_leave_requests()
    return jsonify(response_list_schema.dump(requests_)), 200


@leave_bp.patch("/<uuid:request_id>/review")
@role_required("admin", "hr_manager")
def review_leave(request_id):
    try:
        data = review_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    reviewer_id = get_jwt_identity()
    print(f"Reviewer ID: {reviewer_id}, Request ID: {request_id}, Action: {data['status']}")  # Debugging line
    leave_request = leave_service.review_leave_request(
        request_id, data["status"], reviewer_id
    )
    if not leave_request:
        return jsonify({"message": "Leave request not found"}), 404

    return jsonify(response_schema.dump(leave_request)), 200

@leave_bp.get("/approved")
@jwt_required()
def approved_leave_for_period():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"message": "month and year query params are required"}), 422

    requests_ = leave_service.get_approved_leave_for_period(month, year)
    return jsonify(response_list_schema.dump(requests_)), 200

@leave_bp.get("/balances/my")
@jwt_required()
def my_leave_balances():
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(user_id=user_id).first()
    if not employee:
        return jsonify({"message": "Employee profile not found"}), 404

    year = request.args.get("year", type=int, default=datetime.utcnow().year)
    balances = leave_service.get_leave_balances(employee.id, year)
    return jsonify(balances), 200


@leave_bp.get("/balances")
@role_required("admin", "hr_manager")
def all_leave_balances():
    year = request.args.get("year", type=int, default=datetime.utcnow().year)
    balances = leave_service.get_leave_balances_for_all_employees(year)
    return jsonify(balances), 200