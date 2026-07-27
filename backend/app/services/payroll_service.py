from decimal import Decimal
from app.models import Employee, Payslip
from app.extensions import db

def generate_payslip(data):
    """
    Generates a payslip for the specified employee and period.
    Args:
        data (dict): A dictionary containing the employee ID, period month, and period year.
    Returns:
        Payslip: The generated payslip object.

    """
    employee = Employee.query.filter_by(id=data["employee_id"]).first()
    if not employee:
        raise ValueError("Employee not found")

    existing = Payslip.query.filter_by(
        employee_id=employee.id,
        period_month=data["period_month"],
        period_year=data["period_year"]
        ).first()
    if existing:
        raise ValueError("Payslip already exists for this period")

    # Assuming a standard of 22 working days in a month for simplicity
    working_days_in_period = 22
    paid_days = Decimal(str(working_days_in_period))
    basic_salary = employee.salary or Decimal("0")

    # Calculate gross pay, tax, social security, and net pay
    gross_pay = basic_salary * (paid_days / working_days_in_period)
    tax_amount = Decimal("0")
    social_security_amount = min(gross_pay * Decimal("0.05"), Decimal("500"))
    net_pay = gross_pay - tax_amount - social_security_amount

    payslip = Payslip(
        employee_id=employee.id,
        period_month=data["period_month"],
        period_year=data["period_year"],
        working_days_in_period=working_days_in_period,
        paid_days=paid_days,
        gross_pay=gross_pay,
        tax_amount=tax_amount,
        social_security_amount=social_security_amount,
        net_pay=net_pay,
        status="finalized",
    )

    db.session.add(payslip)
    db.session.commit()
    return payslip

def get_payslips_for_employee(employee_id):
    """
    Retrieves all payslips for the specified employee.
    Args:
        employee_id (str): The ID of the employee.
    Returns:
        list: A list of payslip objects for the employee.
    """
    return Payslip.query.filter_by(employee_id=employee_id).order_by(
        Payslip.period_year.desc(), Payslip.period_month.desc()
        ).all()