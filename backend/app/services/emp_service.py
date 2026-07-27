from app.extensions import db
from app.models import User, Employee, Role

def list_employees(page=1, per_page=20, department_id=None):
    """Lists employees with optional pagination and filtering by department.
    Args:
        page (int): The page number for pagination.
        per_page (int): The number of employees per page.
        department_id (int, optional): The ID of the department to filter employees by.
    Returns:
        tuple: A tuple containing the list of employees and the total count.
    """
    query = Employee.query
    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total

def get_employee_by_id(employee_id):
    return Employee.query.filter_by(id=employee_id).first()

def create_employee(data):
    """Creates a new employee and associated user.
    Args:
        data (dict): A dictionary containing employee and user data.
    Returns:
        tuple: A tuple containing the created employee and an error message (if any).
    """
    # Check if the email is already registered
    if User.query.filter_by(email=data["email"]).first():
        return None, "Email already registered"

    if Employee.query.filter_by(staff_no=data["staff_no"]).first():
        return None, "Staff number already exists"

    # Create the user
    role = Role.query.filter_by(name=data.get("employee")).first()
    if not role:
        role = Role(name=data.get("role_name", "employee"))
        db.session.add(role)
        db.session.flush()

    user = User(email=data["email"], role_id=role.id)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()  # Flush to get the user ID

    # Create the employee
    employee = Employee(
        staff_no=data["staff_no"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data.get("phone_number"),
        hire_date=data.get("hire_date"),
        job_title=data.get("job_title"),
        salary=data.get("salary"),
        employment_status=data.get("employment_status", "active"),
        user_id=user.id,
        department_id=data.get("department_id")
    )
    db.session.add(employee)
    db.session.commit()
    return employee, None

def update_employee(employee_id, data):
    """Updates an existing employee's information.
    Args:
        employee_id (str): The ID of the employee to update.
        data (dict): A dictionary containing the updated employee data.
    Returns:
        tuple: A tuple containing the updated employee and an error message (if any).
    """
    employee = Employee.query.filter_by(id=employee_id).first()
    if not employee:
        return None, "Employee not found"

    # Update fields
    for key, value in data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)

    db.session.commit()
    return employee

def delete_employee(employee_id):
    """Deletes an employee and their associated user.
    Args:
        employee_id (str): The ID of the employee to delete.
    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    employee = Employee.query.filter_by(id=employee_id).first()
    if not employee:
        return False

    # Delete the associated user
    user = employee.user
    db.session.delete(employee)
    if user:
        db.session.delete(user)

    db.session.commit()
    return True