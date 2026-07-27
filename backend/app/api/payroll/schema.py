from marshmallow import Schema, fields


class PayslipGenerateSchema(Schema):
    employee_id = fields.UUID(required=True)
    period_month = fields.Integer(required=True)
    period_year = fields.Integer(required=True)


class PayslipResponseSchema(Schema):
    id = fields.UUID()
    employee_id = fields.UUID()
    period_month = fields.Integer()
    period_year = fields.Integer()
    working_days_in_period = fields.Integer()
    paid_days = fields.Decimal(as_string=True)
    gross_pay = fields.Decimal(as_string=True)
    tax_amount = fields.Decimal(as_string=True)
    social_security_amount = fields.Decimal(as_string=True)
    net_pay = fields.Decimal(as_string=True)
    status = fields.String()
    generated_at = fields.DateTime()