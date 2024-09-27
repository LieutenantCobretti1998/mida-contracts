from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, send_file, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound
from werkzeug.utils import secure_filename
from forms.custom_validators import calculate_new_amount
from forms.filters import *
from forms.edit_contract_form import EditContractForm
from database.db_init import db
from database.validators import SearchEngine, EditContract, ContractManager

check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
@login_required
def get_all_contracts():
    return render_template("check_contracts.html", search_mode=False)


@check_contracts_bp.route('/contract_overview/<int:contract_id>', methods=['GET'])
@login_required
def get_contract(contract_id):
    try:
        search_engine = SearchEngine(db.session, contract_id)
        search_result = search_engine.search_company_with_contract()
        return render_template("check_contract.html",
                               search_result=search_result,
                               contract_id=contract_id
                               )
    except NoResultFound:
        abort(404)


@check_contracts_bp.route('/contract/<int:contract_id>', methods=['GET'])
@login_required
def edit_contract(contract_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    try:
        form = EditContractForm()
        contract_manager = ContractManager(db.session)
        categories = contract_manager.search_categories()
        form.categories.choices = [(category.id, category.category_name) for category in categories]
        search_engine = SearchEngine(db.session, contract_id)
        search_result = search_engine.search_company_with_contract()
        form.categories.default = search_result.category_id
        form.process()
        return render_template("edit_contract.html",
                               search_result=search_result,
                               form=form,
                               contract_id=contract_id,
                               )
    except NoResultFound:
        abort(404)


@check_contracts_bp.route('/update_contract/<int:contract_id>', methods=['POST'])
@login_required
def update_contract(contract_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    search_engine = SearchEngine(db.session, contract_id)
    edit_engine = EditContract(db.session, contract_id)
    contract_manager = ContractManager(db.session)
    categories = contract_manager.search_categories()
    original_data = search_engine.search_company_with_contract()
    form = EditContractForm()
    form.categories.choices = [(category.id, category.category_name) for category in categories]
    form.categories.default = original_data.category_id
    selected_category_id = form.categories.data
    valid_category = next((cat for cat in categories if cat.id == selected_category_id), None)
    if valid_category is None:
        flash('anlış kateqoriya seçilib. Zəhmət olmasa düzgün seçimi edin', 'error')
        return redirect(url_for('all_contracts.edit_contract', contract_id=contract_id))
    if form.validate_on_submit():
        new_remained_amount = None
        file = form.pdf_file.data
        original_start_date = original_data.date
        original_end_date = original_data.end_date
        new_start_date = form.start_date.data
        new_end_date = form.end_date.data
        start_date_changed = new_start_date is not None and new_start_date != original_start_date
        end_date_changed = new_end_date is not None and new_end_date != original_end_date
        new_amount = form.amount.data
        filename = ""
        if start_date_changed and end_date_changed:
            if new_start_date >= new_end_date:
                flash("Başlanğıc tarixi bitmə tarixindən sonra və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, )
        elif start_date_changed:
            if new_start_date >= original_end_date:
                flash("Başlanğıc tarixi original bitmə tarixindən sonra və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data,)
        elif end_date_changed:
            if new_end_date <= original_start_date:
                flash("Bitmə tarixi orijinal başlanğıc tarixindən əvvəl və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, )
        if file:
            filename = secure_filename(make_unique(f"{file.filename}"))
        if (original_data.amount != new_amount) and new_amount:
            try:
                total_addition_amount = edit_engine.calculate_total_contract_addition(contract_id)
                total_act_amount = edit_engine.calculate_total_contract_act(contract_id)
                new_remained_amount = calculate_new_amount(new_amount, total_addition_amount, total_act_amount)
                new_amount += total_addition_amount

            except ValueError:
                flash(
                    "The amount can be less than the original one. Delete the acts in order to increase the remained amount.",
                    "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data,
                                       )

        data_dict = dict(
            company_name=filter_string_fields(
                form.company.data) if form.company.data else original_data.company.company_name,
            voen=filter_voen(form.voen.data) if form.voen.data else original_data.company.voen,
            contract_number=filter_contract_number(
                form.contract_number.data) if form.contract_number.data else original_data.contract_number,
            date=form.start_date.data if form.start_date.data else original_data.date,
            amount=new_amount if new_amount else original_data.amount,
            remained_amount=new_remained_amount if not None else original_data.remained_amount,
            adv_payer=True if form.is_adv_payer.data else False,
            pdf_file_path=filename if form.pdf_file.data else None,
            category_id=form.categories.data if form.categories.data else original_data.category_id,
            end_date=form.end_date.data if form.end_date.data else original_data.end_date

        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file.data)
        if success:
            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_contracts.get_contract', contract_id=contract_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                   search_result=original_data,
                                   )
    else:
        flash("Validation Error. Please check all fields", "error")
        return render_template('edit_contract.html', form=form, contract_id=contract_id, search_result=original_data,
                               )


@check_contracts_bp.route('/preview_pdf/<int:contract_id>', methods=['GET'])
@login_required
def preview_pdf(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    search_result = search_engine.search_company_with_contract()
    try:
        return send_file(search_result.pdf_file_path)
    except FileNotFoundError:
        abort(404)


@check_contracts_bp.route('/delete_contract/<int:contract_id>', methods=['DELETE'])
@login_required
def delete_contract(contract_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
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


@check_contracts_bp.route('/related_contracts/<string:voen>', methods=['GET'])
@login_required
def related_contracts(voen):
    return render_template("check_contracts.html", search_mode=True, voen=voen)
