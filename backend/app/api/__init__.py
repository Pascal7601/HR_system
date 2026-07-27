def register_blueprints(app):
    from app.api.auth.routes import auth_bp
    from app.api.employees.routes import employee_bp
    from app.api.departments.routes import departments_bp
    from app.api.leave.routes import leave_bp
    from app.api.payroll.routes import payroll_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(employee_bp, url_prefix="/api/employees")
    app.register_blueprint(departments_bp, url_prefix="/api/departments")
    app.register_blueprint(leave_bp, url_prefix="/api/leave")
    app.register_blueprint(payroll_bp, url_prefix="/api/payroll")