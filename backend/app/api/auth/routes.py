from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from marshmallow import ValidationError
from app.api.auth.schemas import RegisterSchema, LoginSchema
from app.models import User
from app.services import auth_service

auth_bp = Blueprint('auth', __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()

@auth_bp.post('/register')
def register():
    try:
        data = register_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user, error = auth_service.register_user(data)
    if error:
        return jsonify({"message": error}), 409

    return jsonify({"message": "User registered successfully", "user_id": user.id}), 201

@auth_bp.post('/login')
def login():
    try:
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user, error = auth_service.authenticate_user(data['email'], data['password'])
    if error or not user:
        return jsonify({"message": error or "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role_name": user.role.name})
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name
        }
    }), 200

@auth_bp.post('/me')
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role.name
    }), 200