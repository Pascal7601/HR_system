from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))
    first_name = fields.String(required=True, validate=validate.Length(max=100))
    last_name = fields.String(required=True, validate=validate.Length(max=100))
    role_name = fields.String(validate=validate.Length(max=100), load_default="employee")  # Default role is "employee"


class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))