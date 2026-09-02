# app/models.py
from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Establishes a 1-to-many relationship with Transaction
    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False)

    # Foreign key links directly to user.id
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)