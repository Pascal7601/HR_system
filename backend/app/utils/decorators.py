from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*allowed_roles):
    """
    Decorator to restrict access to routes based on user roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role_name")

            if role not in allowed_roles:
                return {"message": "Access forbidden: insufficient permissions"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator