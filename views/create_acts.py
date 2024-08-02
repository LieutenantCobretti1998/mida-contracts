from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError
from forms.create_act_form import CreateAct
from database.models import *
from database.db_init import db
from database.validators import ContractManager
from forms.custom_validators import add_contract_pdf
from forms.filters import filter_act_number

create_act_bp = Blueprint('create_act', __name__)


# Our create act routes
@create_act_bp.route('/create_act', methods=['GET', 'POST'])
def create_act():
    form = CreateAct()
    return render_template('create_act.html', form=form)


@create_act_bp.route('/save_act', methods=['GET', 'POST'])
def save_act():
    form = CreateAct()
    filtered_act_number = filter_act_number(form.act_number.data)
