from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.api.payroll.schema import PayslipGenerateSchema, PayslipResponseSchema
from app.services import payroll_service
from app.utils.decorators import role_required

payroll_bp = Blueprint("payroll", __name__)

generate_schema = PayslipGenerateSchema()
response_schema = PayslipResponseSchema()
response_list_schema = PayslipResponseSchema(many=True)


@payroll_bp.post("/generate")
@role_required("admin", "hr_manager")
def generate_payslip():
    try:
        data = generate_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    payslip, error = payroll_service.generate_payslip(data)
    if error:
        return jsonify({"message": error}), 400

    return jsonify(response_schema.dump(payslip)), 201


@payroll_bp.get("/employee/<uuid:employee_id>")
@role_required("admin", "hr_manager", "employee")
def get_employee_payslips(employee_id):
    payslips = payroll_service.get_payslips_for_employee(employee_id)
    return jsonify(response_list_schema.dump(payslips)), 200


@payroll_bp.get("/my")
@jwt_required()
def my_payslips():
    user_id = get_jwt_identity()
    payslips = payroll_service.get_payslips_for_user(user_id)
    return jsonify(response_list_schema.dump(payslips)), 200