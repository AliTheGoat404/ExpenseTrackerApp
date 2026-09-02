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

@transactions_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    current_user_id = int(get_jwt_identity())
    user_transactions = (Transaction.query.filter_by(user_id=current_user_id)
                         .order_by(Transaction.date.desc())
                         .all()
                         )
    results = []
    for t in user_transactions:
        results.append(
            {
                "id": t.id,
                "amount": t.amount,
                "category": t.category,
                "description": t.description,
                "date": t.date.isoformat(),
            }
        )

    return {"transactions": results, "total_count": len(results)}, 200

@transactions_bp.route("/transactions/<int:transaction_id>", methods=["PUT"])
@jwt_required()
def update_transaction(transaction_id):
    current_user_id = int(get_jwt_identity())
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
    if not transaction:
        return {"error": "Transaction not found"}, 404

    data = request.get_json(silent=True) or {}

    # Update fields if provided
    if "amount" in data and data["amount"] is not None:
        transaction.amount = data["amount"]
    if "category" in data and data["category"]:
        transaction.category = data["category"]
    if "description" in data:
        transaction.description = data["description"]

    db.session.commit()

    return {"message": "Transaction updated successfully"}, 200

@transactions_bp.route("/transactions/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    current_user_id = int(get_jwt_identity())
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
    if not transaction:
        return {"error": "Transaction not found"}, 404
    db.session.delete(transaction)
    db.session.commit()
    return {"message": "Transaction deleted successfully"}, 200

