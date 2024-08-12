from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError
from forms.create_contract_form import CreateContractForm
from database.models import *
from database.db_init import db
from database.validators import ContractManager
from forms.custom_validators import add_contract_pdf
from forms.filters import *

parameter_bp = Blueprint('parameters', __name__)


@parameter_bp.route('/categories', methods=['GET'])
def categories():
    return render_template('categories.html')