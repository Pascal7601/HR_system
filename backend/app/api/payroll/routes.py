from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.api.payroll.schemas import PayslipGenerateSchema, PayslipResponseSchema
from app.services import payroll_service
from app.utils.decorators import role_required

from flask import send_file

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



@payroll_bp.post("/generate-batch")
@role_required("admin", "hr_manager")
def generate_payslips_batch():
    data = request.get_json() or {}
    month = data.get("period_month")
    year = data.get("period_year")
    if not month or not year:
        return jsonify({"message": "period_month and period_year are required"}), 422

    result = payroll_service.generate_payslips_for_period(month, year)
    return jsonify(result), 201


@payroll_bp.get("/period")
@role_required("admin", "hr_manager")
def get_payslips_by_period():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"message": "month and year query params are required"}), 422

    payslips = payroll_service.get_payslips_for_period(month, year)
    return jsonify(response_list_schema.dump(payslips)), 200


@payroll_bp.get("/my")
@jwt_required()
def my_payslips():
    user_id = get_jwt_identity()
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    payslips = payroll_service.get_payslips_for_employee(user_id, month, year)
    return jsonify(response_list_schema.dump(payslips)), 200

@payroll_bp.get("/export")
@role_required("admin", "hr_manager")
def export_payslips_excel():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    if not month or not year:
        return jsonify({"message": "month and year query params are required"}), 422

    buffer = payroll_service.build_payslips_excel(month, year)
    filename = f"payroll_{year}_{month:02d}.xlsx"

    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )