# HR System

A backend HR management system built with Flask, covering employee records, departments, attendance, leave management, and payroll.

## Project status

🚧 **In progress** — currently at the database design stage.

- [x] Database schema design (ERD)
- [ ] Flask backend scaffolding (app factory, blueprints, models, services)
- [ ] Payroll generation logic (pro-ration, tax brackets, deductions)
- [ ] API testing
- [ ] Authentication/authorization hardening
- [ ] Deployment

## Project description

This system supports core HR operations for a small-to-medium organization:

- **Authentication** — role-based accounts (admin, HR manager, employee) with JWT-based login
- **Employee management** — CRUD on employee records, linked 1:1 to a user account
- **Departments** — grouping of employees, each department optionally has a manager (who is themselves an employee)
- **Leave management** — employees submit leave requests against configurable leave types; HR/managers approve or reject
- **Payroll** — monthly payslip generation per employee, with gross pay pro-rated for unpaid leave and mid-month joiners, statutory-style tax and social security deductions computed from a simple documented formula

## Database design

The ERD was designed in Lucidchart before implementation. See [`backend/docs/erd.png`](backend/docs/erd.png) for the diagram

### Tables

| Table            | Purpose                                                                      |
| ---------------- | ---------------------------------------------------------------------------- |
| `roles`          | Lookup table for access levels (admin, hr_manager, employee)                 |
| `users`          | Login credentials, 1:many with `roles`                                       |
| `employees`      | Core HR record, 1:1 with `users`                                             |
| `departments`    | Groups employees; has an optional manager (self-referencing via `employees`) |
| `attendance`     | Daily check-in/check-out per employee _(not yet implemented)_                |
| `leave_types`    | Lookup table for leave categories (annual, sick, unpaid, etc.)               |
| `leave_requests` | Employee leave applications; reviewed by another employee                    |
| `payslips`       | Monthly pay record per employee, generated from salary + leave data          |

### Key relationships

- One `role` → many `users`
- One `user` → one `employee` (1:1)
- One `department` → many `employees`; one `employee` → zero-or-one `department` as manager (self-referencing loop, handled with a nullable FK)
- One `employee` → many `leave_requests`, `payslips`
- One `leave_type` → many `leave_requests`
- `leave_requests.reviewed_by` → `employees` (not `users`), so reviewer name/title can be shown without an extra join

## Tech stack

- **Backend:** Flask (application factory + blueprints)
- **ORM:** SQLAlchemy + Flask-Migrate (Alembic)
- **Auth:** Flask-JWT-Extended
- **Validation/serialization:** Marshmallow
- **Database:** PostgreSQL (SQLite for local dev)

## Project structure

```
hr-system-backend/
├── app/
```

## Getting started

```bash
git clone <your-repo-url>
cd hr-system/backend
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt

```

## License
