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

def get_payslips_for_employee(employee_id, month=None, year=None):
    """
    Retrieves all payslips for the specified employee.
    Args:
        employee_id (str): The ID of the employee.
    Returns:
        list: A list of payslip objects for the employee.
    """
    employee = Employee.query.filter_by(user_id=employee_id).first()
    if not employee:
        return []
    query = Payslip.query.filter_by(employee_id=employee.id)
    if month:
        query = query.filter_by(period_month=month)
    if year:
        query = query.filter_by(period_year=year)
    return query.order_by(Payslip.period_year.desc(), Payslip.period_month.desc()).all()

def generate_payslips_for_period(month, year):
    """Generate a payslip for every active employee for this period.
    Skips employees who already have one (idempotent) rather than erroring out."""

    employees = Employee.query.filter_by(employment_status="active").all()
    created, skipped = [], []

    for employee in employees:
        existing = Payslip.query.filter_by(
            employee_id=employee.id, period_month=month, period_year=year
        ).first()
        if existing:
            skipped.append(employee.staff_no)
            continue

        payslip = generate_payslip({
            "employee_id": employee.id,
            "period_month": month,
            "period_year": year,
        })
        if payslip:
            created.append(employee.staff_no)

    return {"created": created, "skipped": skipped}

def get_payslips_for_period(month, year):
    return Payslip.query.filter_by(period_month=month, period_year=year).order_by(
        Payslip.generated_at.desc()
    ).all()

import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter


def build_payslips_excel(month, year):
    """Build an in-memory .xlsx workbook of all payslips for a given period."""
    payslips = get_payslips_for_period(month, year)

    wb = Workbook()
    sheet = wb.active
    month_name = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ][month - 1]
    sheet.title = f"Payroll {month_name} {year}"[:31]  # Excel sheet name limit

    headers = [
        "Staff No", "Employee Name", "Working Days", "Paid Days",
        "Gross Pay", "Tax", "Social Security", "Net Pay", "Status",
    ]

    header_font = Font(name="Arial", bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="3D5A4C", end_color="3D5A4C", fill_type="solid")
    body_font = Font(name="Arial")
    currency_format = "$#,##0.00"

    for col_idx, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row_idx, payslip in enumerate(payslips, start=2):
        employee = payslip.employee
        row_values = [
            employee.staff_no if employee else "—",
            employee.first_name + " " + employee.last_name if employee else "Unknown",
            payslip.working_days_in_period,
            float(payslip.paid_days),
            float(payslip.gross_pay),
            float(payslip.tax_amount),
            float(payslip.social_security_amount),
            float(payslip.net_pay),
            payslip.status,
        ]
        for col_idx, value in enumerate(row_values, start=1):
            cell = sheet.cell(row=row_idx, column=col_idx, value=value)
            cell.font = body_font
            if col_idx in (5, 6, 7, 8):  # Gross Pay, Tax, Social Security, Net Pay
                cell.number_format = currency_format

    # Totals row
    if payslips:
        total_row = len(payslips) + 2
        sheet.cell(row=total_row, column=2, value="Total").font = Font(name="Arial", bold=True)
        for col_idx in (5, 6, 7, 8):
            col_letter = get_column_letter(col_idx)
            cell = sheet.cell(
                row=total_row, column=col_idx,
                value=f"=SUM({col_letter}2:{col_letter}{total_row - 1})",
            )
            cell.font = Font(name="Arial", bold=True)
            cell.number_format = currency_format

    # Reasonable column widths instead of Excel's cramped default
    widths = [16, 22, 13, 11, 14, 12, 15, 14, 12]
    for col_idx, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(col_idx)].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer