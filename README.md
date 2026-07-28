# HR System

A backend + frontend HR management system covering employee records, org structure, leave management, and payroll, built with Flask (REST API) and a plain HTML/JS/CSS frontend.

## Table of contents

- Features
- Tech stack
- Database design
- Running locally
- What was prioritized, and why
- Payroll formula and assumptions
- Business rules and thresholds
- What I'd improve given more time

## Features

**Employees**

- CRUD on employee records: name, job title, department, employment type (full-time/part-time/contract), employment status, hire date, salary
- Soft delete only — an employee is marked `terminated`, never removed from the database, so payslip and leave history stay intact and auditable
- Direct-manager reporting line (`manager_id`), separate from department ownership, powering a recursive org chart view

**Auth**

- JWT-based login (access + refresh tokens), roles: `admin`, `hr_manager`, `employee`
- Role-based access control on every protected route via a `role_required()` decorator reading the JWT's role claim

**Departments**

- Grouping of employees, each with an optional manager
- Nullable manager FK specifically to break the circular insert dependency (a department needs a manager who is an employee; an employee needs a department that may need a manager) — handled with SQLAlchemy's `post_update=True`

**Leave management**

- Employees submit leave requests against configurable leave types (annual, sick, unpaid); HR/managers approve or reject
- Leave balances (used vs. remaining days per type, per employee), computed on the fly rather than stored, so they're always correct against the source data
- "Who's out and when" view, scoped to a selected period, visible to everyone (not just HR)

**Payroll**

- Monthly payslip generation per employee: pro-rated gross pay, marginal tax-bracket deduction, flat capped social security, net pay
- Batch generation for an entire period in one action (idempotent — skips employees who already have a payslip for that period instead of erroring)
- Excel export of a period's payroll via `openpyxl`, with currency formatting and a live `SUM()` totals formula

**Dashboard (frontend)**

- Role-aware views: HR/admin sees org-wide data and approval/generation controls; employees see only their own data
- Sections: my profile, pending approvals (HR), who's out/when, leave balances, payslips for a selected period, org chart
- Consistent loading / empty / error states across every section

## Tech stack

- **Backend:** Flask (application factory pattern + blueprints), SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended, Flask-Cors, Marshmallow
- **Database:** SQLite (all primary/foreign keys stored as `String(36)` UUIDs — deliberately no PostgreSQL-specific types, since this project isn't targeting production deployment)
- **Frontend:** Plain HTML, CSS, and vanilla JavaScript (`fetch`-based API client, no framework)
- **Excel export:** `openpyxl`

## Database design

The ERD was designed in Lucidchart before any code was written — see [`backend/docs/erd.png`](backend/docs/erd.png) for the diagram

### Tables

| Table            | Purpose                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `roles`          | Lookup table for access levels (admin, hr_manager, employee)                                                         |
| `users`          | Login credentials, 1:many with `roles`                                                                               |
| `employees`      | Core HR record, 1:1 with `users`; self-referencing `manager_id` for direct reporting line                            |
| `departments`    | Groups employees; has an optional manager (references `employees`, nullable to break the circular insert dependency) |
| `leave_types`    | Lookup table for leave categories (annual, sick, unpaid, etc.)                                                       |
| `leave_requests` | Employee leave applications; reviewed by another employee                                                            |
| `payslips`       | Monthly pay record per employee, generated from salary + leave data                                                  |

### Key relationships

- One `role` → many `users`
- One `user` → one `employee` (1:1)
- One `department` → many `employees`; one `employee` → zero-or-one `department` as manager (self-referencing loop, handled with a nullable FK + `post_update=True`)
- One `employee` → many `leave_requests`, `payslips`
- One `employee` → many `direct_reports` (self-referencing `manager_id`, distinct from `departments.manager_id`)
- One `leave_type` → many `leave_requests`
- `leave_requests.reviewed_by` → `employees` (not `users`), so reviewer name/title can be shown without an extra join

## Running locally

### Backend

Navigate into the backend folder and set up a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
FLASK_APP=wsgi
FLASK_ENV=development
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me-too
DATABASE_URL=sqlite:///dev.db
```

Then run the migrations and start the server:

```bash
flask db init          # only the very first time
flask db migrate -m "initial migration"
flask db upgrade
python seed.py          # optional: creates roles, leave types, and a few sample users
python run.py
```

The API runs at `http://127.0.0.1:5000`. Health check: `GET /health`.

### Frontend

No build step — just open `frontend/login.html` directly in a browser, or serve the folder with any static server:

```bash
cd frontend
```

Update `API_BASE` in `js/api.js` if your backend runs on a different host/port.

## What was prioritized, and why

Given limited time, the order was: get the data model right first, then payroll correctness, then the dashboard.

1. **Database design before any code** — the ERD was worked out and reviewed in Lucidchart (relationships, cardinalities, nullable FKs for circular dependencies) before writing a single model, since fixing a wrong foreign key after data exists is far more expensive than fixing it on a whiteboard.
2. **Payroll math over payroll polish** — the actual tax/pro-ration logic was treated as the highest-value piece to get right, since it's the part of the brief with concrete, checkable correctness (marginal brackets, mid-month joiners, unpaid leave). Excel export and batch generation were built only after the underlying formula was solid.
3. **Soft delete from day one** — rather than retrofitting it later, `employment_status`-based deactivation was decided before the `Employee` model was even finalized, since it affects the shape of every relationship touching payroll/leave history.
4. **Org structure (`manager_id`) added deliberately separate from `Department.manager_id`** — these look similar but answer different questions ("who runs this department" vs. "who does this specific person report to"), and conflating them would have made the org chart wrong for anyone whose manager isn't their department head.
5. **Leave-coverage safeguards were consciously deprioritized.** The brief calls for identifying and addressing real-world leave problems (team under-coverage, requests sitting unanswered, insufficient notice). Given the time available, this was set aside in favor of finishing the core CRUD + payroll + dashboard loop end-to-end rather than partially building both. See "What I'd improve" below for what this would involve.

## Payroll formula and assumptions

Documented in code as well (`app/services/payroll_service.py`), repeated here for visibility.

Assumptions (illustrative, not modeled on any real country's tax code):

- Working days = Monday–Friday within the calendar month. Public holidays are **not** excluded.
- An employee is only paid from their `hire_date` onward if it falls inside the period being processed — days before that simply aren't counted as owed (handles mid-month joiners).
- Only leave of type `"unpaid"` reduces pay. Approved `"annual"`/`"sick"` leave does **not** reduce `paid_days` — that's the entire point of those leave types.
- Tax is calculated **marginally**: each bracket's rate applies only to the slice of income within that bracket, not the whole salary at one flat rate.

Tax brackets (monthly, made up for this exercise):

| Range           | Rate |
| --------------- | ---- |
| $0 – $1,000     | 0%   |
| $1,000 – $3,000 | 10%  |
| $3,000+         | 20%  |

Social security: flat 5% of gross pay, capped at $500/month.

Formula:

```
working_days_in_period = count of weekdays in the month
effective_start          = max(period_start, employee.hire_date)
paid_days                = weekdays(effective_start, period_end) − unpaid_leave_weekdays
gross_pay                = basic_salary × (paid_days / working_days_in_period)
tax_amount                = marginal_bracket_tax(gross_pay)
social_security_amount   = min(gross_pay × 5%, $500)
net_pay                   = gross_pay − tax_amount − social_security_amount
```

How the required edge cases are handled:

- **Mid-month joiners** — fall out naturally from `effective_start`; no special-case branch.
- **Zero-deduction cases** — any `gross_pay` ≤ $1,000 produces `tax_amount = 0.00` because the marginal-bracket loop contributes nothing from the 0% bracket and never reaches a taxed one.
- **Salary near a bracket boundary** — because tax is sliced per-bracket rather than looked-up-and-applied-flat, moving from $2,999 to $3,001 changes tax by cents, not by suddenly taxing the whole salary at a higher rate.

## Business rules and thresholds

What's currently enforced:

- A payslip can only be generated once per employee per period (`UNIQUE(employee_id, period_month, period_year)` at the DB level, plus an application-level check before insert).
- Employees can only be soft-deleted (`employment_status = "terminated"`), never hard-deleted — cascading deletes were deliberately removed from `Employee.leave_requests`/`Employee.payslips` so a hard delete attempt is rejected by the foreign key constraint rather than silently wiping history.
- Every write-protected route checks the caller's JWT role against an explicit allow-list (`role_required("admin", "hr_manager")`, etc.) rather than relying on the frontend to hide buttons.

What's explicitly not yet enforced (see next section): minimum notice period for leave requests, team-coverage checks when approving leave, and stale/unanswered request handling. Right now, `create_leave_request()` accepts any date range with no validation beyond `end_date >= start_date`.

## What I'd improve given more time

1. **Leave safeguards (the main known gap).** Specifically:
   - Minimum notice period — reject or flag leave requests submitted with fewer than N days' notice (configurable per leave type; sick leave obviously needs an exception).
   - Team under-coverage guard — before approving, check what percentage of a department is already approved-off overlapping those dates, and warn (or block) if it crosses a threshold.
   - Stale request handling — a request sitting in `pending` for more than N days should surface more prominently (e.g. sorted to the top, or an "overdue" badge), since silently-ignored requests are a real spreadsheet failure mode this system should catch.
2. **A `tax_brackets` table** instead of hardcoded values, so rates are configurable/auditable per year without a code change.
3. **A `holidays` calendar** so `working_days_in_period` excludes public holidays, not just weekends.
4. **Automated tests** — none exist yet; the project was verified manually end-to-end. Unit tests for `payroll_service.apply_marginal_brackets()` and `_count_weekdays()` specifically would be high-value given how easy off-by-one bracket/date bugs are to introduce silently.
5. **A real "submit leave" form on the frontend** — the button and role-based visibility exist, but the modal/form behind it was deprioritized in favor of finishing payroll correctness first.
6. **Pagination on the org chart** — fine for a small team, but a `get_org_chart()` that recursively serializes every active employee would need pagination or lazy-loading at real company scale.
