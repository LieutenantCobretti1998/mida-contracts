from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for
from sqlalchemy.exc import OperationalError, IntegrityError
from forms.create_contract_form import CreateContractForm
from database.models import *
from database.db_init import db
from forms.filters import (filter_string_fields, filter_voen, get_or_create_company, check_voen,
                           filter_contract_number, check_voen_contract_company_exists)

create_contract_bp = Blueprint('create_contract', __name__)


# Our create_contract routes
@create_contract_bp.route('/create_contract', methods=["GET", 'POST'])
def create_contract():
    form = CreateContractForm()
    return render_template("add_contract.html", form=form)


@create_contract_bp.route('/save_contract', methods=["POST"])
def save_contract():
    form = CreateContractForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        company_name = filter_string_fields(form.company.data)
        company = get_or_create_company(company_name)
        voen_id = check_voen(form.voen.data, company.id)

        if isinstance(voen_id, dict) and voen_id["status"] is None:
            flash(f"VOEN is already linked to "
                  f"{db.session.query(Companies).filter_by(id=voen_id["company_id"]).one().company_name} "
                  f"company", "warning")
            return render_template('add_contract.html', form=form)

        if check_voen_contract_company_exists(voen_id, form.contract_number.data, float(form.amount.data)):
            flash("A contract with the same voen, contract_number and amount is already existed", "warning")
            return render_template('add_contract.html', form=form)
        try:
            contract = Contract(contract_number=filter_contract_number(form.contract_number.data), date=form.date.data,
                                voen_id=voen_id if isinstance(voen_id, int) else voen_id.id, amount=float(form.amount.data))
            db.session.add(contract)
            db.session.commit()
            flash("The contract is saved successfully!", "success")
            return redirect(url_for("create_contract.create_contract"))
        except OperationalError as e:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
            return render_template('add_contract.html', form=form)
    else:
        flash("Something went wrong", "error")
        return render_template('add_contract.html', form=form)