# app/__init__.py
from flask import Flask

from app.config import Config
from app.extensions import db, jwt, migrate


def create_app(config_class=Config):
    # 1. Instantiate the Flask application object
    app = Flask(__name__)
    app.config.from_object(config_class)
    #What it does: Reads all upper-case variables defined in our Config class (like SQLALCHEMY_DATABASE_URI) and injects them directly into Flask's internal app.config dictionary.

    # 2. Bind the pre-created extensions to this specific app instance
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 3. Import and register Blueprints locally inside the factory
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)

    return app