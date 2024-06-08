from flask import Flask
from configuration import *
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
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    from views.create_contract import create_contract_bp
    app.register_blueprint(create_contract_bp)
    from views.check_contracts import check_contracts_bp
    app.register_blueprint(check_contracts_bp)
    # initialize of flask app and db
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db, render_as_batch=True)
    with app.app_context():
        db.create_all()
    return app
