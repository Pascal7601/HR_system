from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.api.leave.schema import (
    LeaveRequestCreateSchema,
    LeaveReviewSchema,
    LeaveRequestResponseSchema,
)
from app.services import leave_service
from app.utils.decorators import role_required

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
    leave_request, error = leave_service.create_leave_request(user_id, data)
    if error:
        return jsonify({"message": error}), 400

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
    requests_ = leave_service.get_pending_requests()
    return jsonify(response_list_schema.dump(requests_)), 200


@leave_bp.patch("/<uuid:request_id>/review")
@role_required("admin", "hr_manager")
def review_leave(request_id):
    try:
        data = review_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    reviewer_id = get_jwt_identity()
    leave_request, error = leave_service.review_leave_request(
        request_id, data["status"], reviewer_id
    )
    if error:
        return jsonify({"message": error}), 404

    return jsonify(response_schema.dump(leave_request)), 200