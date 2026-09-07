from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return {}, 200

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 409

    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully"}, 201


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return {}, 200

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    # 1. Single indexed query
    user = User.query.filter_by(username=username).first()

    # 2. Fast check: don't attempt hashing if user doesn't exist
    if not user or not check_password_hash(user.password, password):
        return {"error": "Invalid username or password"}, 401

    # 3. Create access token and return complete user object
    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "Logged in successfully",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }, 200