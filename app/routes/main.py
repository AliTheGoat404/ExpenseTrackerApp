# app/routes/main.py
from flask import Blueprint

# 1. Create the Blueprint instance
main_bp = Blueprint("main", __name__)


# 2. Add general routes
@main_bp.route("/")
def home():
    return {"message": "Expense Tracker API is connected and running!"}, 200


@main_bp.route("/health")
def health_check():
    return {"status": "healthy"}, 200