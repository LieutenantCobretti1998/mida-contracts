import flask_wtf
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, send_file, abort
from werkzeug.utils import secure_filename
from forms.contract_search import SearchContract
from forms.filters import *
from forms.edit_contract_form import EditContractForm
from database.db_init import db
from database.validators import SearchEngine, EditContract, ContractManager

check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    return render_template("check_contracts.html")


@check_contracts_bp.route('/contract/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    form = EditContractForm()
    search_engine = SearchEngine(db.session, contract_id)
    search_result = search_engine.search_company_with_contract()
    return render_template("check_contract.html",
                           search_result=search_result,
                           contract_id=contract_id,
                           form=form)


@check_contracts_bp.route('/update_contract/<int:contract_id>', methods=['POST'])
def update_contract(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    edit_engine = EditContract(db.session, contract_id)
    original_data = search_engine.search_company_with_contract()
    form = EditContractForm()
    if form.validate_on_submit():
        file = form.pdf_file.data
        filename = ""
        if file:
            filename = secure_filename(make_unique(f"{original_data.company.voen}_{file.filename}"))
        data_dict = dict(
            contract_number=filter_contract_number(
                form.contract_number.data) if form.contract_number.data else original_data.contract_number,
            date=form.date.data if form.date.data else original_data.date,
            amount=float(form.amount.data) if form.amount.data else original_data.amount,
            adv_payer=True if form.is_adv_payer.data == "Yes" else False,
            pdf_file_path=filename if form.pdf_file.data else None,
            company_name=filter_string_fields(
                form.company.data) if form.company.data else original_data.company.company_name,
            voen=filter_voen(form.voen.data) if form.voen.data else original_data.company.voen,

        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file.data)
        if success:
            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_contracts.get_contract', contract_id=contract_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return redirect(url_for('all_contracts.get_contract', contract_id=contract_id))
    else:
        errors = {field.name: field.errors for field in form}
        return jsonify(errors=errors, success=False)


@check_contracts_bp.route('/preview_pdf/<int:contract_id>', methods=['GET'])
def preview_pdf(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    contract_result = search_engine.search_company_with_contract()
    try:
        if contract_result and contract_result.pdf_file_path:
            return send_file(contract_result.pdf_file_path)
    except FileNotFoundError:
        abort(404)


@check_contracts_bp.route('/delete_contract/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id):
    contract_manager = ContractManager(db.session)
    contract_on_delete = contract_manager.delete_contract(contract_id)
    if contract_on_delete:
        db.session.commit()
        flash("Contract deleted successfully", "success")
        return jsonify({
            'status': 'success',
        }), 200
    else:
        flash("Could not delete the contract. Something went wrong on the server side", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500


# @check_contracts_bp.route('/related_contracts/<string:voen>', methods=['GET'])
# def related_contracts(voen):
#     form = SearchContract()
#     page = request.args.get("page", 1, type=int)
#     search_query = voen
#     return handle_search(search_query, form, page=page)
