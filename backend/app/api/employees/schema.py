from marshmallow import Schema, fields, validate

class EmployeeCreateSchema(Schema):
    id = fields.Int(dump_only=True)
    staff_no = fields.Str(required=True, validate=validate.Length(min=1))
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    phone_number = fields.Str(validate=validate.Length(min=10, max=15))
    date_of_birth = fields.Date()
    hire_date = fields.Date(load_default=None)
    job_title = fields.Str(load_default=None)
    salary = fields.Decimal(as_string=True, load_default=None)
    employment_status = fields.Str(validate=validate.OneOf(["active", "inactive"]))
    user_id = fields.Int(required=True)
    department_id = fields.UUID(required=False, allow_none=True)