from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from backend.app.api.departments.schemas import DepartmentSchema
from app.extensions import db
from app.models import Department
from app.utils.decorators import role_required

departments_bp = Blueprint("departments", __name__)
schema = DepartmentSchema()
list_schema = DepartmentSchema(many=True)


@departments_bp.get("")
@role_required("admin", "hr_manager", "employee")
def list_departments():
    departments = Department.query.all()
    return jsonify(list_schema.dump(departments)), 200


@departments_bp.get("/<uuid:dept_id>")
@role_required("admin", "hr_manager", "employee")
def get_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    return jsonify(schema.dump(department)), 200


@departments_bp.post("")
@role_required("admin", "hr_manager")
def create_department():
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    department = Department(**data)
    db.session.add(department)
    db.session.commit()
    return jsonify(schema.dump(department)), 201


@departments_bp.put("/<uuid:dept_id>")
@role_required("admin", "hr_manager")
def update_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    try:
        data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for key, value in data.items():
        setattr(department, key, value)
    db.session.commit()
    return jsonify(schema.dump(department)), 200


@departments_bp.delete("/<uuid:dept_id>")
@role_required("admin")
def delete_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    db.session.delete(department)
    db.session.commit()
    return "", 204