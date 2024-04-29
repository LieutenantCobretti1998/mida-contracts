from flask import Flask
from configuration import WTF_CSRF_SECRET_KEY, APP_SECRET_KEY, TEST_DB_URI
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database.db_init import db
from database.models import *

# Initialization of the app


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = WTF_CSRF_SECRET_KEY
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URI
    from views.create_contract import create_contract_bp
    app.register_blueprint(create_contract_bp)
    # initialize of flask app and db
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()
    return app
