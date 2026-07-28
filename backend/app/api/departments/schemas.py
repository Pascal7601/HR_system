from marshmallow import Schema, fields

class DepartmentSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    manager_id = fields.UUID(load_default=None, allow_none=True)