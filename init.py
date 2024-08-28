from flask import Flask
from configuration import *
from flask_migrate import Migrate
from database.db_init import db
from extensions import login_manager


# Initialization of the app


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = WTF_CSRF_SECRET_KEY
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DB_URI
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["UPLOAD_FOLDER_ACTS"] = UPLOAD_FOLDER_ACTS
    app.config["UPLOAD_FOLDER_ADDITIONS"] = UPLOAD_FOLDER_ADDITIONS
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1000 * 1000
    from views.login import login_bp
    app.register_blueprint(login_bp)
    from views.dashboard import home_bp
    app.register_blueprint(home_bp)
    from views.create_contract import create_contract_bp
    app.register_blueprint(create_contract_bp, url_prefix="/contracts")
    from views.check_contracts import check_contracts_bp
    app.register_blueprint(check_contracts_bp, url_prefix="/contracts")
    from views.check_acts import check_acts_bp
    app.register_blueprint(check_acts_bp, url_prefix="/acts")
    from views.table_api import api_contracts_bp, api_companies_bp, api_acts_bp, api_categories_bp, api_additions_bp, api_dashboard_bp
    app.register_blueprint(api_dashboard_bp, url_prefix="/api")
    app.register_blueprint(api_contracts_bp, url_prefix="/api")
    app.register_blueprint(api_companies_bp, url_prefix="/api")
    app.register_blueprint(api_acts_bp, url_prefix="/api")
    app.register_blueprint(api_categories_bp, url_prefix="/api")
    app.register_blueprint(api_additions_bp, url_prefix="/api")
    from views.create_company import create_company_bp
    app.register_blueprint(create_company_bp, url_prefix="/companies")
    from views.check_companies import check_companies_bp
    app.register_blueprint(check_companies_bp, url_prefix="/companies")
    from views.create_acts import create_act_bp
    app.register_blueprint(create_act_bp, url_prefix="/acts")
    from views.create_additions import create_addition_bp
    app.register_blueprint(create_addition_bp, url_prefix="/additions")
    from views.check_additions import check_additions_bp
    app.register_blueprint(check_additions_bp, url_prefix="/additions")
    from views.parameters import parameter_bp
    app.register_blueprint(parameter_bp, url_prefix="/parameters")
    # initialize of flask app and db
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login.login"
    migrate = Migrate()
    migrate.init_app(app, db, render_as_batch=True)
    with app.app_context():
        db.create_all()
    return app
