from marshmallow import Schema, fields, validate

class EmployeeCreateSchema(Schema):
    id = fields.Int(dump_only=True)
    staff_no = fields.Str(required=True, validate=validate.Length(min=1))
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    phone_number = fields.Str(validate=validate.Length(min=10, max=15))
    date_of_birth = fields.Date(load_default=None)
    hire_date = fields.Date(load_default=None)
    job_title = fields.Str(load_default=None)
    salary = fields.Decimal(as_string=True, load_default=None)
    user_id = fields.Int(required=True)
    department_id = fields.UUID(required=False, allow_none=True)

class EmployeeUpdateSchema(Schema):
    first_name = fields.String()
    last_name = fields.String()
    phone_number = fields.String()
    job_title = fields.String()
    salary = fields.Decimal(as_string=True)
    department_id = fields.UUID()
    employment_status = fields.String(
        validate=validate.OneOf(["active", "on_leave", "terminated"])
    )

class EmployeeResponseSchema(Schema):
    id = fields.UUID()
    employee_code = fields.String()
    full_name = fields.String()
    job_title = fields.String()
    employment_status = fields.String()
    department_id = fields.UUID()
    hire_date = fields.Date()
    salary = fields.Decimal(as_string=True)