from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions", methods=["POST"])
@jwt_required()
def create_transaction():
    data = request.get_json(silent=True) or {}

    if data.get("amount") is None or not data.get("category"):
        return {"error": "Amount and category are required"}, 400

    # Retrieve identity (user ID) stored inside the token during login
    current_user_id = int(get_jwt_identity())

    transaction = Transaction(
        amount=data.get("amount"),
        category=data.get("category"),
        description=data.get("description"),
        date=datetime.now(timezone.utc),
        user_id=current_user_id,
    )

    db.session.add(transaction)
    db.session.commit()

    return {"message": "Transaction created successfully"}, 201