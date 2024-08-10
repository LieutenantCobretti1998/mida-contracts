from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError
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
    adv_payer = True if form.is_adv_payer.data else False
    if form.validate():
        try:
            file = form.pdf_file.data
            filename = secure_filename(file.filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER'], filename, filtered_company_name)
            company = contract_manager.get_or_create_company(filtered_company_name, filtered_voen)
            contract = Contract(
                contract_number=filtered_contract,
                date=form.date.data,
                amount=float(form.amount.data),
                company_id=company.id,
                adv_payer=adv_payer,
                pdf_file_path=file_path
            )
            db.session.add(contract)
            db.session.commit()
            file.save(file_path)
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
