import os

from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, send_file, abort, json, current_app, \
    request
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound
from werkzeug.utils import secure_filename
from forms.custom_validators import calculate_new_amount, add_contract_pdf
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
        category = search_result.category.category_name
        additional_files = json.loads(search_result.pdf_file_paths) if search_result.pdf_file_paths else []
        return render_template("check_contract.html",
                               search_result=search_result,
                               contract_id=contract_id,
                               category=category,
                               additional_files=additional_files
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
        if search_result.pdf_file_paths:
            file_paths = json.loads(search_result.pdf_file_paths)
            # Create a list of tuples: (index, full file path, file name)
            additional_files = [
                (
                    i,
                    fp,
                    os.path.basename(fp).split("_", 1)[1] if "_" in os.path.basename(fp) else os.path.basename(fp)
                )
                for i, fp in enumerate(file_paths)
            ]
        else:
            additional_files = []
        form.categories.default = search_result.category_id
        form.start_date.default = search_result.date
        form.end_date.default = search_result.end_date
        form.process()

        return render_template("edit_contract.html",
                               search_result=search_result,
                               form=form,
                               contract_id=contract_id,
                               additional_files=additional_files
                               )
    except NoResultFound:
        abort(404)


@check_contracts_bp.route('/update_contract/<int:contract_id>', methods=['POST'])
@login_required
def update_contract(contract_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    allowed_extensions = (".pdf", ".gif", ".png", ".jpeg", ".jpg")
    search_engine = SearchEngine(db.session, contract_id)
    edit_engine = EditContract(db.session, contract_id)
    contract_manager = ContractManager(db.session)
    categories = contract_manager.search_categories()
    original_data = search_engine.search_company_with_contract()
    old_additional_files_data = enumerate(json.loads(original_data.pdf_file_paths)) if original_data.pdf_file_paths else []
    old_additional_files = list(enumerate(old_additional_files_data))
    form = EditContractForm()
    form.categories.choices = [(category.id, category.category_name) for category in categories]
    form.categories.default = original_data.category_id
    selected_category_id = form.categories.data
    valid_category = next((cat for cat in categories if cat.id == selected_category_id), None)
    if valid_category is None:
        flash('Anlış kateqoriya seçilib. Zəhmət olmasa düzgün seçimi edin', 'error')
        return redirect(url_for('all_contracts.edit_contract', contract_id=contract_id))
    if form.validate_on_submit():
        new_remained_amount = None
        new_files = {}
        file_objects = {}
        file = form.pdf_file.data
        original_start_date = original_data.date
        original_end_date = original_data.end_date

        new_start_date = form.start_date.data
        new_end_date = form.end_date.data
        start_date_changed = new_start_date is not None and new_start_date != original_start_date
        end_date_changed = new_end_date is not None and new_end_date != original_end_date
        new_amount = form.amount.data
        additional_files = form.additional_files.data
        if not additional_files:
            for i, old_path in enumerate(old_additional_files):
                field_name = f"updated_file_{i}"
                uploaded_file = request.files.get(field_name)
                if uploaded_file:
                    filename_lower = secure_filename(uploaded_file.filename.lower())
                    if not filename_lower.endswith(allowed_extensions):
                        flash(f"Fayl icazə verilən formatda deyil: {uploaded_file.filename}", "error")
                        return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                               search_result=original_data, additional_files=old_additional_files )
                    # Here you may want to append the new file's details to your lists/dicts for further processing
                    # For example, adding to new_files and file_objects or directly appending to a list of file paths
                    new_files[i] = make_unique(filename_lower)
                    file_objects[i] = uploaded_file

            for i in range(len(old_additional_files), 5):
                new_field = f"new_file_{i}"
                new_file = request.files.get(new_field)
                if new_file:
                    new_filename = secure_filename(new_file.filename.lower())
                    if not new_filename.endswith(allowed_extensions):
                        flash(f"Fayl icazə verilən formatda deyil: {new_file.filename}", "error")
                        return render_template(
                            'edit_contract.html',
                            form=form,
                            contract_id=contract_id,
                            search_result=original_data,
                            additional_files=old_additional_files
                        )
                    # Here you may want to append the new file's details to your lists/dicts for further processing
                    # For example, adding to new_files and file_objects or directly appending to a list of file paths
                    new_files[i] = make_unique(new_filename)
                    file_objects[i] = new_file
        else:
            additional_file_paths = []
            for additional_file in additional_files:
                additional_filename = secure_filename(additional_file.filename)
                additional_file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER'], additional_filename,
                                                        original_data.company.company_name)
                additional_file.save(additional_file_path)
                additional_file_paths.append(additional_file_path)
            serialized_file_paths = json.dumps(additional_file_paths)
            original_data.pdf_file_paths = serialized_file_paths
        print(new_files)
        filename = ""
        if form.comments.data is not None:
            stripped_comments = form.comments.data.strip()
            if stripped_comments == '':
                comments = None  # User input only whitespace; set to None
            else:
                comments = stripped_comments  # Use the stripped comment
        else:
            comments = original_data.comments  # Field not submitted; keep original comment

        if start_date_changed and end_date_changed:
            if new_start_date >= new_end_date:
                flash("Başlanğıc tarixi bitmə tarixindən sonra və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, additional_files=old_additional_files)
        elif start_date_changed:
            if new_start_date >= original_end_date:
                flash("Başlanğıc tarixi original bitmə tarixindən sonra və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, additional_files=old_additional_files)
        elif end_date_changed:
            if new_end_date <= original_start_date:
                flash("Bitmə tarixi orijinal başlanğıc tarixindən əvvəl və ya ona bərabər ola bilməz", "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, additional_files=old_additional_files)
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
                    "Yeni məbləğ orijinal məbləğdən az ola bilər. Qalan məbləği artırmaq üçün aktları silin",
                    "warning")
                return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                       search_result=original_data, additional_files=old_additional_files
                                       )
        data_dict = dict(
            company_name=filter_string_fields(
                form.company.data) if form.company.data else original_data.company.company_name,
            voen=filter_voen(form.voen.data) if form.voen.data else original_data.company.voen,
            contract_number=filter_contract_number(
                form.contract_number.data) if form.contract_number.data else original_data.contract_number,
            date=form.start_date.data if form.start_date.data else original_data.date,
            amount=new_amount if new_amount else original_data.amount,
            remained_amount=new_remained_amount if new_remained_amount else original_data.remained_amount,
            adv_payer=True if form.is_adv_payer.data else False,
            is_expired = True if form.status.data else False,
            pdf_file_path=filename if form.pdf_file.data else None,
            pdf_file_paths = new_files if new_files else None ,
            comments = comments,
            category_id=form.categories.data if form.categories.data else original_data.category_id,
            end_date=form.end_date.data if form.end_date.data else original_data.end_date

        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file.data, file_objects)
        if success:
            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_contracts.get_contract', contract_id=contract_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return render_template('edit_contract.html', form=form, contract_id=contract_id,
                                   search_result=original_data, additional_files=old_additional_files
                                   )
    else:
        flash("Doğrulama xətası. Zəhmət olmasa, bütün sahələri yoxlayın.", "error")
        return render_template('edit_contract.html', form=form, contract_id=contract_id, search_result=original_data, additional_files=old_additional_files
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

@check_contracts_bp.route('/delete_pdf/<int:contract_id>/<int:pdf_id>', methods=['DELETE'])
@login_required
def delete_pdf(contract_id, pdf_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)

    search_engine = SearchEngine(db.session, contract_id)
    try:
        search_engine.delete_pdf(pdf_id)
        flash("Əlavə fayl uğurla silindi", "success")
        return jsonify({
            "redirect": url_for('all_contracts.get_contract', contract_id=contract_id)
        })
    except FileNotFoundError:
        abort(404)
    except Exception as e:
        print(e)
        flash("Müqaviləni silmək mümkün olmadı", "error")
        return jsonify({"redirect": url_for('all_contracts.get_contract', contract_id=contract_id)}), 500

@check_contracts_bp.route('/preview_additional_pdf/<path:document_name>', methods=['GET'])
@login_required
def preview_additional_pdf(document_name):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # Create the absolute path of the file directly using the document_name
    if not upload_folder.startswith(upload_folder):
        abort(403)
    try:
        return send_file(document_name)
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
        flash("Müqavilə uğurla silindi", "success")
        return jsonify({
            'status': 'success',
        }), 200
    else:
        flash("Müqaviləni silmək mümkün olmadı", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500


@check_contracts_bp.route('/related_contracts/<string:voen>', methods=['GET'])
@login_required
def related_contracts(voen):
    return render_template("check_contracts.html", search_mode=True, voen=voen)
