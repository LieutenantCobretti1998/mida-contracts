from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError, IntegrityError
from forms.create_contract_form import CreateContractForm
from database.models import *
from database.db_init import db
from database.validators import ContractManager
from forms.custom_validators import add_contract_pdf
from forms.filters import *

create_contract_bp = Blueprint('create_contract', __name__)


# Our create_contract routes
@create_contract_bp.route('/create_contract', methods=["GET", 'POST'])
def create_contract():
    form = CreateContractForm()
    return render_template("add_contract.html", form=form)


@create_contract_bp.route('/save_contract', methods=["POST"])
def save_contract():
    form = CreateContractForm()
    filtered_company_name = filter_string_fields(form.company.data)
    filtered_voen = filter_voen(form.voen.data)
    filtered_contract = filter_contract_number(form.contract_number.data)
    contract_manager = ContractManager(db.session)
    if form.validate():
        try:
            file = form.pdf_file.data
            voen = form.voen.data
            filename = secure_filename(file.filename)
            print(filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER'], filtered_company_name, filename, voen)
            print(file_path)
            company = contract_manager.get_or_create_company(filtered_company_name, filtered_voen)
            contract = Contract(contract_number=filtered_contract,
                                date=form.date.data,
                                amount=float(form.amount.data),
                                company_id=company.id,
                                pdf_file_path=file_path
                                )
            file.save(file_path)
            db.session.add(contract)
            db.session.commit()
            flash("The contract is saved successfully!", "success")
            return redirect(url_for("create_contract.create_contract"))

        except ValueError as e:
            flash(str(e), "warning")
        except OperationalError:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
    else:
        flash("Validation Error. Please check all fields", "error")
    return render_template('add_contract.html', form=form)
