from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User

# Create the Blueprint instance named 'auth'
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    if not data.get("username") or not data.get("password"):
        return {"error": "Username and password are required"}, 400

    if User.query.filter_by(username=data.get("username")).first():
        return {"error": "Username already exists"}, 409

    hashed_password = generate_password_hash(data.get("password"))
    user = User(username=data.get("username"), password=hashed_password)

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully"}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    if not data.get("username") or not data.get("password"):
        return {"error": "Username and password are required"}, 400

    user = User.query.filter_by(username=data.get("username")).first()
    if not user or not check_password_hash(user.password, data.get("password")):
        return {"error": "Invalid username or password"}, 401

    # Store user.id in the JWT identity so it can be cast to int safely in transaction routes
    access_token = create_access_token(identity=str(user.id))

    return {"message": "Logged in successfully", "access_token": access_token}, 200