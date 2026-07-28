import uuid
from datetime import datetime, date
from app import create_app
from app.extensions import db
from app.models import Role, User, Department, Employee, Leave

app = create_app("dev")


def get_or_create_role(name):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(id=str(uuid.uuid4()), name=name)
        db.session.add(role)
        db.session.flush()
    return role


def get_or_create_leave_type(name, default_days):
    leave_type = Leave.query.filter_by(name=name).first()
    if not leave_type:
        leave_type = Leave(id=str(uuid.uuid4()), name=name, default_days_per_year=default_days)
        db.session.add(leave_type)
        db.session.flush()
    return leave_type


def seed():
    with app.app_context():
        db.create_all()
        # --- Roles ---
        admin_role = get_or_create_role("admin")
        hr_role = get_or_create_role("hr_manager")
        dept_mgr_role = get_or_create_role("dept_manager")
        employee_role = get_or_create_role("employee")

        # --- Leave Types ---
        get_or_create_leave_type("annual", 21)
        get_or_create_leave_type("sick", 10)
        get_or_create_leave_type("unpaid", 0)

        db.session.commit()

        # --- Departments ---
        departments_data = [
            {"name": "Engineering", "description": "Software development and tech operations"},
            {"name": "Human Resources", "description": "Talent acquisition and employee relations"},
        ]

        dept_map = {}
        for d in departments_data:
            dept = Department.query.filter_by(name=d["name"]).first()
            if not dept:
                dept = Department(id=str(uuid.uuid4()), name=d["name"], description=d["description"])
                db.session.add(dept)
                db.session.commit()
            dept_map[d["name"]] = dept

        # --- Admin User ---
        if not User.query.filter_by(email="admin@vunohglobal.com").first():
            admin_user = User(id=str(uuid.uuid4()), email="admin@vunohglobal.com", role_id=admin_role.id)
            admin_user.set_password("AdminPass123!")
            db.session.add(admin_user)
            db.session.commit()
            print("Created admin user: admin@vunohglobal.com / AdminPass123!")

        # --- Managers (Jane Miller & Sarah Connor) ---
        managers_data = [
            {
                "staff_no": "MGR-0001",
                "first_name": "Jane",
                "last_name": "Miller",
                "email": "jane.miller@vunohglobal.com",
                "job_title": "Engineering Director",
                "salary": 8500,
                "role": dept_mgr_role,
                "dept": dept_map["Engineering"],
            },
            {
                "staff_no": "MGR-0002",
                "first_name": "Sarah",
                "last_name": "Connor",
                "email": "sarah.connor@vunohglobal.com",
                "job_title": "HR Director",
                "salary": 7500,
                "role": hr_role,
                "dept": dept_map["Human Resources"],
            },
        ]

        mgr_obj_map = {}

        for m in managers_data:
            mgr_employee = Employee.query.filter_by(staff_no=m["staff_no"]).first()
            if not mgr_employee:
                mgr_user = User(id=str(uuid.uuid4()), email=m["email"], role_id=m["role"].id)
                mgr_user.set_password("ManagerPass123!")
                db.session.add(mgr_user)
                db.session.flush()

                mgr_employee = Employee(
                    id=str(uuid.uuid4()),
                    staff_no=m["staff_no"],
                    first_name=m["first_name"],
                    last_name=m["last_name"],
                    job_title=m["job_title"],
                    salary=m["salary"],
                    employment_status="active",
                    department_id=m["dept"].id,
                    user_id=mgr_user.id,
                    manager_id=None,  # Directors/Managers have no direct manager assigned here
                )
                db.session.add(mgr_employee)
                db.session.commit()

                # Link manager back to department
                m["dept"].manager_id = mgr_employee.id
                db.session.commit()
                print(f"Created manager: {m['email']} / ManagerPass123!")

            mgr_obj_map[m["staff_no"]] = mgr_employee

        # --- Regular Employees (Reporting to specific Managers) ---
        jane_id = mgr_obj_map["MGR-0001"].id
        sarah_id = mgr_obj_map["MGR-0002"].id

        employees_data = [
            # Engineering Team (Reporting to Jane Miller)
            {"staff_no": "EMP-0001", "first_name": "John", "last_name": "Doe", "email": "john.doe@vunohglobal.com", "title": "Senior Software Engineer", "salary": 5500, "type": "full_time", "dept": dept_map["Engineering"], "mgr_id": jane_id},
            {"staff_no": "EMP-0002", "first_name": "Alice", "last_name": "Smith", "email": "alice.smith@vunohglobal.com", "title": "Frontend Developer", "salary": 4500, "type": "full_time", "dept": dept_map["Engineering"], "mgr_id": jane_id},
            {"staff_no": "EMP-0003", "first_name": "Bob", "last_name": "Johnson", "email": "bob.johnson@vunohglobal.com", "title": "Backend Developer", "salary": 4800, "type": "full_time", "dept": dept_map["Engineering"], "mgr_id": jane_id},
            {"staff_no": "EMP-0004", "first_name": "Charlie", "last_name": "Brown", "email": "charlie.brown@vunohglobal.com", "title": "DevOps Consultant", "salary": 5200, "type": "contract", "dept": dept_map["Engineering"], "mgr_id": jane_id},
            {"staff_no": "EMP-0005", "first_name": "Diana", "last_name": "Prince", "email": "diana.prince@vunohglobal.com", "title": "QA Engineer", "salary": 4200, "type": "part_time", "dept": dept_map["Engineering"], "mgr_id": jane_id},
            {"staff_no": "EMP-0006", "first_name": "Ethan", "last_name": "Hunt", "email": "ethan.hunt@vunohglobal.com", "title": "Fullstack Developer", "salary": 5000, "type": "full_time", "dept": dept_map["Engineering"], "mgr_id": jane_id},

            # HR Team (Reporting to Sarah Connor)
            {"staff_no": "EMP-0007", "first_name": "Fiona", "last_name": "Gallagher", "email": "fiona.gallagher@vunohglobal.com", "title": "HR Specialist", "salary": 3800, "type": "full_time", "dept": dept_map["Human Resources"], "mgr_id": sarah_id},
            {"staff_no": "EMP-0008", "first_name": "George", "last_name": "Clark", "email": "george.clark@vunohglobal.com", "title": "Recruiter", "salary": 3600, "type": "full_time", "dept": dept_map["Human Resources"], "mgr_id": sarah_id},
            {"staff_no": "EMP-0009", "first_name": "Hannah", "last_name": "Abbott", "email": "hannah.abbott@vunohglobal.com", "title": "Talent Consultant", "salary": 4100, "type": "contract", "dept": dept_map["Human Resources"], "mgr_id": sarah_id},
            {"staff_no": "EMP-0010", "first_name": "Ian", "last_name": "Malcolm", "email": "ian.malcolm@vunohglobal.com", "title": "HR Operations Assistant", "salary": 3400, "type": "part_time", "dept": dept_map["Human Resources"], "mgr_id": sarah_id},
        ]

        for e in employees_data:
            if not Employee.query.filter_by(staff_no=e["staff_no"]).first():
                emp_user = User(id=str(uuid.uuid4()), email=e["email"], role_id=employee_role.id)
                emp_user.set_password("EmployeePass123!")
                db.session.add(emp_user)
                db.session.flush()

                employee = Employee(
                    id=str(uuid.uuid4()),
                    staff_no=e["staff_no"],
                    first_name=e["first_name"],
                    last_name=e["last_name"],
                    job_title=e["title"],
                    salary=e["salary"],
                    employment_status="active",
                    department_id=e["dept"].id,
                    manager_id=e["mgr_id"],  # Self-referential direct manager key
                    user_id=emp_user.id,
                )
                db.session.add(employee)
                db.session.commit()
                print(f"Created employee: {e['email']} (Reports to: {e['mgr_id']})")

        print("\nRefined Seeding Complete!")


if __name__ == "__main__":
    seed()