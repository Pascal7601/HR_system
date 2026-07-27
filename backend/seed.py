import uuid

from app import create_app
from app.extensions import db
from app.models import Role, User, Department, Employee, Leave

app = create_app("dev")


def get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.session.add(role)
        db.session.flush()
    return role


def get_or_create_leave_type(name, default_days):
    leave_type = Leave.query.filter_by(name=name).first()
    if not leave_type:
        leave_type = Leave(name=name, default_days_per_year=default_days)
        db.session.add(leave_type)
    return leave_type


def seed():
    with app.app_context():
        # --- Roles ---
        admin_role = get_or_create_role("admin")
        hr_role = get_or_create_role("hr_manager")
        employee_role = get_or_create_role("employee")

        # --- Leave types ---
        get_or_create_leave_type("annual", 21)
        get_or_create_leave_type("sick", 10)
        get_or_create_leave_type("unpaid", 0)

        db.session.commit()

        # --- Department (created first, manager added after employee exists) ---
        engineering = Department.query.filter_by(name="Engineering").first()
        if not engineering:
            engineering = Department(name="Engineering", description="Product engineering team")
            db.session.add(engineering)
            db.session.commit()

        # --- Admin user (no employee record needed) ---
        if not User.query.filter_by(email="admin@hrsystem.com").first():
            admin_user = User(email="admin@hrsystem.com", role_id=admin_role.id)
            admin_user.set_password("AdminPass123!")
            db.session.add(admin_user)
            db.session.commit()
            print("Created admin user: admin@hrsystem.com / AdminPass123!")

        # --- Manager (employee + user) ---
        manager_employee = Employee.query.filter_by(staff_no="EMP-0001").first()
        if not manager_employee:
            manager_user = User(email="jane.manager@hrsystem.com", role_id=hr_role.id)
            manager_user.set_password("ManagerPass123!")
            db.session.add(manager_user)
            db.session.flush()  # get manager_user.id before using it

            manager_employee = Employee(
                staff_no="EMP-0001",
                first_name="Jane",
                last_name="Manager",
                job_title="Engineering Manager",
                salary=8000,
                department_id=engineering.id,
                user_id=manager_user.id,
            )
            db.session.add(manager_employee)
            db.session.commit()

            # Now that the manager employee exists, link them to the department
            engineering.manager_id = manager_employee.id
            db.session.commit()
            print("Created manager: jane.manager@hrsystem.com / ManagerPass123!")

        # --- Regular employee ---
        if not Employee.query.filter_by(staff_no="EMP-0002").first():
            emp_user = User(email="john.doe@hrsystem.com", role_id=employee_role.id)
            emp_user.set_password("EmployeePass123!")
            db.session.add(emp_user)
            db.session.flush()

            employee = Employee(
                staff_no="EMP-0002",
                first_name="John",
                last_name="Doe",
                job_title="Software Engineer",
                salary=5000,
                department_id=engineering.id,
                user_id=emp_user.id,
            )
            db.session.add(employee)
            db.session.commit()
            print("Created employee: john.doe@hrsystem.com / EmployeePass123!")

        print("Seeding complete.")


if __name__ == "__main__":
    seed()