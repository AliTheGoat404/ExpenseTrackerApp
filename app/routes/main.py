# app/routes/main.py
from flask import Blueprint, current_app, send_from_directory

# 1. Create the Blueprint instance
main_bp = Blueprint("main", __name__)


# 2. Serve the frontend dashboard at the root URL
@main_bp.route("/")
def home():
    return send_from_directory(current_app.static_folder, "index.html")


@main_bp.route("/health")
def health_check():
    return {"status": "healthy"}, 200