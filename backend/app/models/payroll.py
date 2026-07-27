import uuid
from app.extensions import db
from datetime import datetime


class Payslip(db.Model):
    __tablename__ = 'payslips'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    working_days_in_period = db.Column(db.Integer, nullable=False)

    # Days actually paid: working days minus unpaid leave minus days before
    # hire_date for mid-month joiners. Drives the pro-rated gross_pay calc.
    paid_days = db.Column(db.Numeric(4, 1), nullable=False)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    social_security_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    status = db.Column(db.String(50), default='draft')  # e.g., draft, finalized, paid
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', back_populates='payslips')

    __table_args__ = (
        db.UniqueConstraint('employee_id', 'period_month', 'period_year', name='unique_employee_period'),
    )

    def __repr__(self):
        return f'<Payslip {self.id} for Employee {self.employee_id}: {self.period_month}/{self.period_year}>'