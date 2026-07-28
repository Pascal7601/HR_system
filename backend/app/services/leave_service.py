from app.extensions import db
from app.models import  Employee, LeaveRequest
from calendar import monthrange
from datetime import date
from app.models import Leave

def _get_employee_for_user(user_id):
    return Employee.query.filter_by(user_id=user_id).first()

def create_leave_request(user_id, data):
    """Creates a leave request for the employee associated with the given user ID.
    Args:
        user_id (int): The ID of the user making the leave request.
        data (dict): A dictionary containing leave request data.
    Returns:
        LeaveRequest: The created leave request.
    """
    employee = _get_employee_for_user(user_id)
    if not employee:
        raise ValueError("Employee record not found for the user.")

    if data['end_date'] < data['start_date']:
        raise ValueError("End date cannot be before start date.")

    leave_request = LeaveRequest(
        employee_id=employee.id,
        leave_type_id=str(data["leave_type_id"]),
        start_date=data["start_date"],
        end_date=data["end_date"],
        reason=data.get("reason", "")
    )
    db.session.add(leave_request)
    db.session.commit()
    return leave_request

def get_leave_requests_for_user(user_id):
    """Retrieves all leave requests for the employee associated with the given user ID.
    Args:
        user_id (int): The ID of the user whose leave requests are to be retrieved.
    Returns:
        list: A list of leave requests for the employee.
    """
    employee = _get_employee_for_user(user_id)
    if not employee:
        return []

    return LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.created_at.asc()).all()

def get_pending_leave_requests():
    """Retrieves all pending leave requests for review.
    Returns:
        list: A list of pending leave requests.
    """
    return LeaveRequest.query.filter_by(status='pending').order_by(LeaveRequest.created_at.asc()).all()

def review_leave_request(request_id, action, reviewer_id):
    """Reviews a leave request by approving or rejecting it.
    Args:
        request_id (int): The ID of the leave request to be reviewed.
        action (str): The action to take ('approve' or 'reject').
        reviewer_id (int): The ID of the user reviewing the leave request.
    Returns:
        LeaveRequest: The updated leave request.
    """
    leave_request = LeaveRequest.query.get(str(request_id))
    if not leave_request:
        raise ValueError("Leave request not found.")

    if action == 'approved':
        leave_request.status = 'approved'
    elif action == 'rejected':
        leave_request.status = 'rejected'
    else:
        raise ValueError("Invalid action. Please specify 'approved' or 'rejected'.")
    leave_request.reviewer_id = reviewer_id

    db.session.commit()
    return leave_request

def get_approved_leave_for_period(month, year):
    """Retrieves all approved leave requests for a specific month and year.
    Args:
        month (int): The month for which to retrieve approved leave requests.
        year (int): The year for which to retrieve approved leave requests.
    Returns:
        list: A list of approved leave requests for the specified period.
    """
    period_start = date(year, month, 1)
    period_end = date(year, month, monthrange(year, month)[1])

    return LeaveRequest.query.filter(
        LeaveRequest.status == "approved",
        LeaveRequest.start_date <= period_end,
        LeaveRequest.end_date >= period_start,
    ).order_by(LeaveRequest.start_date.asc()).all()


def get_leave_balances(employee_id, year):
    leave_types = Leave.query.all()
    approved_requests = LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == "approved",
        db.extract("year", LeaveRequest.start_date) == year,
    ).all()

    used_by_type = {}
    for req in approved_requests:
        used_by_type[req.leave_type_id] = used_by_type.get(req.leave_type_id, 0) + req.duration

    balances = []
    for lt in leave_types:
        used = used_by_type.get(lt.id, 0)
        balances.append({
            "leave_type_id": lt.id,
            "leave_type_name": lt.name,
            "default_days_per_year": lt.default_days_per_year,
            "used_days": used,
            "remaining_days": max(lt.default_days_per_year - used, 0),
        })
    return balances


def get_leave_balances_for_all_employees(year):
    employees = Employee.query.filter_by(employment_status="active").all()
    return [
        {
            "employee_id": emp.id,
            "employee_name": emp.first_name + " " + emp.last_name,
            "balances": get_leave_balances(emp.id, year),
        }
        for emp in employees
    ]