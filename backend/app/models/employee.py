import uuid
from app.extensions import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_title = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Numeric(10, 2), nullable=True)
    employment_status = db.Column(db.String(50), default='active')  # e.g., active, on leave, terminated

    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='employee')

    # Nullable: new hires may not be assigned to a department yet
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'), nullable=True)
    department = db.relationship('Department', back_populates='employees', foreign_keys=[department_id])

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'