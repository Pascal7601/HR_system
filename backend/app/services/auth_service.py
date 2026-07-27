import email

from app.extensions import db
from app.models import User, Role

def register_user(data):
    """Registers a new user with the provided data.
    Args:
        data (dict): A dictionary containing user registration data.
    Returns:
        tuple: A tuple containing the registered user and an error message (if any).
    """

    # check if the email is already registered
    if User.query.filter_by(email=data["email"]).first():
        return None, "Email already registered"

    role = Role.query.filter_by(name=data["role_name"]).first()
    if not role:
        role = Role(name=data["role_name"])
        db.session.add(role)
        db.session.flush()

    user = User(email=data["email"], role_id=role.id)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return user, None

def authenticate_user(email, password):
    """Authenticates a user with the provided email and password.
    Args:
        email (str): The user's email address.
        password (str): The user's password.
    Returns:
        tuple: A tuple containing the authenticated user and an error message (if any).
    """
    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not user.check_password(password):
        return None, "Invalid email or password"
    return user, None

def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()