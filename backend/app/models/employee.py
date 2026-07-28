import uuid
from app.extensions import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    staff_no = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_title = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Numeric(10, 2), nullable=True)
    employment_status = db.Column(db.String(50), default='active')  # e.g., active, on leave, terminated

    # Direct reporting line -- who THIS employee reports to. Distinct from
    # Department.manager_id, which only tracks who runs the department as a
    # whole. Two people in the same department can report to different leads;
    # this field is what actually answers "who reports to whom" for an org chart.
    manager_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=True)
    manager = db.relationship(
        "Employee", remote_side=[id], foreign_keys=[manager_id], backref="direct_reports"
    )


    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='employee')

    # Nullable: new hires may not be assigned to a department yet
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id'), nullable=True)
    department = db.relationship('Department', back_populates='employees', foreign_keys=[department_id])

    leave_requests = db.relationship('LeaveRequest', back_populates='employee', foreign_keys='LeaveRequest.employee_id')
    reviewed_leave_requests = db.relationship('LeaveRequest', back_populates='reviewer', foreign_keys='LeaveRequest.reviewer_id')
    payslips = db.relationship('Payslip', back_populates='employee')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'