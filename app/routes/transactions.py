from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.schemas import TransactionSchema
from app.extensions import db
from app.models import Transaction

transactions_bp = Blueprint("transactions", __name__)
transaction_schema = TransactionSchema()


@transactions_bp.route("/transactions", methods=["POST", "OPTIONS"])
def create_transaction():
    if request.method == "OPTIONS":
        return {}, 200

    @jwt_required()
    def _create():
        raw_data = request.get_json(silent=True) or {}

        try:
            data = transaction_schema.load(raw_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        current_user_id = int(get_jwt_identity())

        transaction = Transaction(
            amount=data["amount"],
            category=data["category"].strip(),
            description=data.get("description", "").strip(),
            date=datetime.now(timezone.utc),
            user_id=current_user_id,
        )

        db.session.add(transaction)
        db.session.commit()

        return {"message": "Transaction created successfully"}, 201

    return _create()


@transactions_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    current_user_id = int(get_jwt_identity())

    query = (
        Transaction.query
        .filter_by(user_id=current_user_id)
        .order_by(Transaction.date.desc())
    )

    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)

    start_date = request.args.get("start_date")
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(Transaction.date >= start_dt)
        except ValueError:
            return {"error": "Invalid start_date format. Use YYYY-MM-DD"}, 400

    end_date = request.args.get("end_date")
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
            query = query.filter(Transaction.date <= end_dt)
        except ValueError:
            return {"error": "Invalid end_date format. Use YYYY-MM-DD"}, 400

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    results = [
        {
            "id": t.id,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
            "date": t.date.isoformat(),
        }
        for t in pagination.items
    ]

    return {
        "transactions": results,
        "pagination": {
            "total_records": pagination.total,
            "current_page": pagination.page,
            "total_pages": pagination.pages,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }, 200


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["PUT", "OPTIONS"])
def update_transaction(transaction_id):
    if request.method == "OPTIONS":
        return {}, 200

    @jwt_required()
    def _update():
        current_user_id = int(get_jwt_identity())
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
        if not transaction:
            return {"error": "Transaction not found"}, 404

        raw_data = request.get_json(silent=True) or {}
        if not raw_data:
            return {"error": "No input data provided"}, 400

        try:
            data = transaction_schema.load(raw_data, partial=True)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        if "amount" in data:
            transaction.amount = data["amount"]
        if "category" in data:
            transaction.category = data["category"].strip()
        if "description" in data:
            transaction.description = data["description"].strip()

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"error": "Database error"}, 500

        return {"message": "Transaction updated successfully"}, 200

    return _update()


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["DELETE", "OPTIONS"])
def delete_transaction(transaction_id):
    if request.method == "OPTIONS":
        return {}, 200

    @jwt_required()
    def _delete():
        current_user_id = int(get_jwt_identity())
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user_id).first()
        if not transaction:
            return {"error": "Transaction not found"}, 404

        db.session.delete(transaction)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"error": "Database error"}, 500

        return {"message": "Transaction deleted successfully"}, 200

    return _delete()