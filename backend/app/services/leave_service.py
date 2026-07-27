from app.extensions import db
from app.models import  Employee, LeaveRequest

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
        leave_type_id=data["leave_type_id"],
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

def review_leave_request(request_id, reviewer_id, action):
    """Reviews a leave request by approving or rejecting it.
    Args:
        request_id (int): The ID of the leave request to be reviewed.
        reviewer_id (int): The ID of the user reviewing the leave request.
        action (str): The action to take ('approve' or 'reject').
    Returns:
        LeaveRequest: The updated leave request.
    """
    leave_request = LeaveRequest.query.get(request_id)
    if not leave_request:
        raise ValueError("Leave request not found.")

    if action == 'approve':
        leave_request.status = 'approved'
    elif action == 'reject':
        leave_request.status = 'rejected'
    else:
        raise ValueError("Invalid action. Please specify 'approve' or 'reject'.")
    leave_request.reviewer_id = reviewer_id

    db.session.commit()
    return leave_request