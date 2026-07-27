from app.extensions import db
import uuid
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Nullable: a department may not have a manager assigned yet, and the
    # manager must be inserted as an employee before this FK can be set
    # (breaks the department <-> employee circular dependency on insert).
    manager_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=True)
    manager = db.relationship('Employee', foreign_keys=[manager_id], post_update=True)
    employees = db.relationship('Employee', back_populates='department', foreign_keys='Employee.department_id')

    def __repr__(self):
        return f'<Department {self.name}>'