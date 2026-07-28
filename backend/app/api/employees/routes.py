from flask import jsonify, request, Blueprint
from app.models import Employee
from marshmallow import ValidationError
from app.api.employees.schemas import (
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeResponseSchema
)
from app.services import emp_service
from app.utils.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity

employee_bp = Blueprint('employee', __name__)

create_schema = EmployeeCreateSchema()
update_schema = EmployeeUpdateSchema()
response_schema = EmployeeResponseSchema()
response_schema_many = EmployeeResponseSchema(many=True)

@employee_bp.get('')
@role_required('admin', 'hr_manager')
def list_employees():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    department_id = request.args.get('department_id', type=int)
    employees, total = emp_service.list_employees(page, per_page, department_id)
    return jsonify(
        {
            "data": response_schema_many.dump(employees),
            "total": total,
            "page": page,
            "per_page": per_page
        }
    ), 200

@employee_bp.get('/<int:employee_id>')
@role_required('admin', 'hr_manager')
def get_employee(employee_id):
    employee = emp_service.get_employee_by_id(employee_id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404
    return response_schema.jsonify(employee), 200

@employee_bp.post('')
@role_required('admin', 'hr_manager')
def create_employee():
    try:
        data = create_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    employee, error = emp_service.create_employee(data)
    if error:
        return jsonify({"message": error}), 400

    return response_schema.jsonify(employee), 201

@employee_bp.put('/<int:employee_id>')
@role_required('admin', 'hr_manager')
def update_employee(employee_id):
    try:
        data = update_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    employee, error = emp_service.update_employee(employee_id, data)
    if error:
        return jsonify({"message": error}), 400

    return response_schema.jsonify(employee), 200

@employee_bp.delete('/<int:employee_id>')
@role_required('admin', 'hr_manager')
def delete_employee(employee_id):
    success, error = emp_service.delete_employee(employee_id)
    if not success:
        return jsonify({"message": error}), 400
    return jsonify({"message": "Employee status updated to 'terminated'"}), 200

@employee_bp.get("/org-chart")
@role_required("admin", "hr_manager", "employee")
def org_chart():
    return jsonify(emp_service.get_org_chart()), 200

@employee_bp.get("/me")
@jwt_required()
def my_profile():
    user_id = get_jwt_identity()
    print('user id', user_id)
    employee = emp_service.get_employee_by_user_id(user_id)
    print('employeee', employee)
    if not employee:
        return jsonify({"message": "Employee profile not found"}), 404
    return jsonify(response_schema.dump(employee)), 200