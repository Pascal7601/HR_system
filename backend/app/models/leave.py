from app.extensions import db
import uuid
from datetime import datetime


class Leave(db.Model):
    __tablename__ = 'leave_types'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    default_days_per_year = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f'<Leave {self.name}>'

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.String(36), db.ForeignKey('leave_types.id'), nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')  # e.g., pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Points to employees, not users: the reviewer is displayed by name/title
    reviewer_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=True)

    employee = db.relationship('Employee', back_populates='leave_requests', foreign_keys=[employee_id])
    leave_type = db.relationship('Leave', back_populates='leave_requests', foreign_keys=[leave_type_id])
    reviewer = db.relationship('Employee', back_populates='reviewed_leave_requests', foreign_keys=[reviewer_id])

    @property
    def duration(self):
        """Calculate the duration of the leave request in days."""
        return (self.end_date - self.start_date).days + 1  # +1 to include both start and end dates

    def __repr__(self):
        return f'<LeaveRequest {self.id} for Employee {self.employee_id}: {self.status}>'