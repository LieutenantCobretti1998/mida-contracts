from flask import Blueprint, render_template, redirect, flash, url_for, current_app, abort
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError, NoResultFound, DBAPIError
from forms.create_addition_form import CreateAddition
from database.validators import ActsManager, ActsSearchEngine
from database.db_init import db
from forms.custom_validators import add_contract_pdf, check_amount
from forms.filters import filter_act_number

create_addition_bp = Blueprint('create_addition', __name__)


# Our create act routes
@create_addition_bp.route('/create_addition', methods=['GET'])
def create_addition():
    form = CreateAddition()
    return render_template('create_addition.html', form=form)