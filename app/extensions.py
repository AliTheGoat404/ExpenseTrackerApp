# app/extensions.py
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Create tool instances without binding them to an app context yet
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()