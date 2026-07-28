from marshmallow import Schema, fields, validate


class EmployeeCreateSchema(Schema):
    employee_code = fields.String(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone_number = fields.String(load_default=None)
    date_of_birth = fields.Date(load_default=None)
    hire_date = fields.Date(load_default=None)
    job_title = fields.String(load_default=None)
    employment_type = fields.String(
        load_default="full_time",
        validate=validate.OneOf(["full_time", "part_time", "contract"]),
    )
    salary = fields.Decimal(load_default=None, as_string=True)
    department_id = fields.String(load_default=None)
    manager_id = fields.String(load_default=None)

    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class EmployeeUpdateSchema(Schema):
    first_name = fields.String()
    last_name = fields.String()
    phone_number = fields.String()
    job_title = fields.String()
    employment_type = fields.String(
        validate=validate.OneOf(["full_time", "part_time", "contract"])
    )
    salary = fields.Decimal(as_string=True)
    department_id = fields.String()
    manager_id = fields.String()
    employment_status = fields.String(
        validate=validate.OneOf(["active", "on_leave", "terminated"])
    )


class EmployeeResponseSchema(Schema):
    id = fields.String()
    employee_code = fields.String()
    full_name = fields.String()
    job_title = fields.String()
    employment_status = fields.String()
    employment_type = fields.String()
    department_id = fields.String()
    manager_id = fields.String()
    manager_name = fields.Method("get_manager_name")
    hire_date = fields.Date()
    salary = fields.Decimal(as_string=True)

    def get_manager_name(self, obj):
        return obj.manager.full_name if obj.manager else None