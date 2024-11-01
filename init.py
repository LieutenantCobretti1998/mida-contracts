import logging
from datetime import timedelta, datetime, timezone
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from configuration import *
from flask_migrate import Migrate
from database.db_init import db
from database.models import Contract
from extensions import login_manager
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
scheduler = BackgroundScheduler()
# Initialization of the app

LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)  # Create log folder if it doesn't exist

# Set up logging to only include time and message
logger = logging.getLogger("ExpiredContractsLogger")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(os.path.join(LOG_FOLDER, 'expired_contracts.log'))
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

def update_expired_contracts():
    try:
        # Get the current time and calculate the cutoff date (contracts that expired more than 1 second ago)
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(seconds=1)

        # Query contracts that have end_date older than the cutoff_time and is_expired is False
        expired_contracts = db.session.query(Contract).filter(
            Contract.end_date <= cutoff_time,
            Contract.is_expired == False
        ).all()

        # Update is_expired status and log the information
        if expired_contracts:
            for contract in expired_contracts:
                contract.is_expired = True
                logger.info(f"Contract ID {contract.id} marked as expired.")

            # Commit the changes to the database
            db.session.commit()
            logger.info(f"{len(expired_contracts)} contracts have been marked as expired.")
        else:
            logger.info("No contracts expired exactly 1 second ago.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while updating expired contracts: {e}")

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = WTF_CSRF_SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = PRODUCTION_DB_URI
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["UPLOAD_FOLDER_ACTS"] = UPLOAD_FOLDER_ACTS
    app.config["UPLOAD_FOLDER_ADDITIONS"] = UPLOAD_FOLDER_ADDITIONS
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
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
    from views.table_api import (api_contracts_bp, api_companies_bp, api_acts_bp, api_categories_bp, api_additions_bp,
                                 api_dashboard_bp, api_users_bp)
    app.register_blueprint(api_dashboard_bp, url_prefix="/api")
    app.register_blueprint(api_contracts_bp, url_prefix="/api")
    app.register_blueprint(api_companies_bp, url_prefix="/api")
    app.register_blueprint(api_acts_bp, url_prefix="/api")
    app.register_blueprint(api_categories_bp, url_prefix="/api")
    app.register_blueprint(api_additions_bp, url_prefix="/api")
    app.register_blueprint(api_users_bp, url_prefix="/api")
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
    csrf.init_app(app)
    with app.app_context():
        db.create_all()

    def scheduler_job():
        with app.app_context():
            update_expired_contracts()

    # Add the job to the scheduler
    if not scheduler.running:
        scheduler.start()
    # Schedule the job to run daily at midnight
    scheduler.add_job(func=scheduler_job, trigger='cron', hour="*", minute=0, id='update_expired_contracts')
    return app
