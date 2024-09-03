from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database.db_init import db
from database.validators import DashBoard

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET'])
@login_required
def home():
    print(current_user.username)
    print(current_user.role)
    dashboard_instance = DashBoard(db.session)
    results = dashboard_instance.get_card_information()
    return render_template("dashboard.html", results=results)
