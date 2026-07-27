from marshmallow import Schema, fields, validate


class LeaveRequestCreateSchema(Schema):
    leave_type_id = fields.UUID(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    reason = fields.String(load_default=None)


class LeaveReviewSchema(Schema):
    status = fields.String(
        required=True, validate=validate.OneOf(["approved", "rejected"])
    )


class LeaveRequestResponseSchema(Schema):
    id = fields.UUID()
    employee_id = fields.UUID()
    leave_type_id = fields.UUID()
    start_date = fields.Date()
    end_date = fields.Date()
    total_days = fields.Integer()
    reason = fields.String()
    status = fields.String()
    created_at = fields.DateTime()