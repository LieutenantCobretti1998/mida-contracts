from flask import Blueprint, render_template, redirect, flash, url_for, abort, send_file, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import NoResultFound, DBAPIError, OperationalError
from database.validators import AdditionManager, AdditionSearchEngine, EditAddition
from database.db_init import db
from forms.edit_addition import EditAdditionForm
from forms.filters import *

check_additions_bp = Blueprint('all_additions', __name__)


# Our roots for acts
@check_additions_bp.route('/act_addition/<int:addition_id>', methods=['GET'])
@login_required
def get_addition(addition_id):
    try:
        search_engine = AdditionSearchEngine(db.session, addition_id)
        search_result = search_engine.search_addition()
        return render_template("check_addition.html",
                               search_result=search_result,
                               addition_id=addition_id
                               )
    except NoResultFound:
        abort(404)


@check_additions_bp.route('/addition/<int:addition_id>', methods=['GET'])
@login_required
def edit_addition(addition_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    try:
        form = EditAdditionForm()
        search_engine = AdditionSearchEngine(db.session, addition_id)
        search_result = search_engine.search_addition()
        return render_template("edit_addition.html",
                               search_result=search_result,
                               addition_id=addition_id,
                               form=form)
    except NoResultFound:
        abort(404)


@check_additions_bp.route('/update_act/<int:addition_id>', methods=['POST'])
@login_required
def update_addition(addition_id):
    search_engine = AdditionSearchEngine(db.session, addition_id)
    edit_engine = EditAddition(db.session, addition_id)
    original_data = search_engine.search_addition()
    form = EditAdditionForm()

    if form.validate_on_submit():
        if form.addition_amount.data and form.contract_id.data == original_data.contract_id:
            try:
                difference = original_data.amount - form.addition_amount.data
                match difference > 0:
                    case True:
                        remained_amount = original_data.amount - difference
                        new_total_amount = original_data.contract.amount - difference
                        edit_engine.change_old_contract(remained_amount, new_total_amount, original_data.contract_id)
                        return
                    case False:
                        remained_amount = original_data.amount - difference * -1
                        new_total_amount = original_data.contract.amount - difference * -1
                        edit_engine.change_old_contract(remained_amount, new_total_amount, original_data.contract_id)
                        return

            except NoResultFound:
                abort(404)
            except (DBAPIError, OperationalError):
                flash("Verilənlər bazasında xəta baş verdi", "error")
                return render_template('edit_act.html', form=form, addition_id=addition_id, search_result=original_data)
        file = form.pdf_file_act.data
        filename = ""
        if file:
            filename = secure_filename(make_unique(f"{file.filename}"))
        data_dict = dict(
            addition_number=filter_act_number(form.addition_number.data) if form.addition_number.data else original_data.addition_number,
            pdf_file_path=filename if file else None,
            date=form.addition_date.data if form.addition_date.data else original_data.date,
            amount=form.addition_amount.data if form.addition_amount.data else original_data.amount,
            contract_id=form.contract_id.data if form.contract_id.data else original_data.contract_id,
        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file_act.data)
        if success:

            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_contracts.get_contract', contract_id=form.contract_id.data))
        else:
            db.session.rollback()
            flash(message, "warning")
            return render_template('edit_addition.html', form=form, addition_id=addition_id,
                                   search_result=original_data,
                                   )
    else:
        flash("Doğrulama Xətası. Bütün sahələri yoxlayın", "error")
        return render_template('edit_addition.html', form=form, addition_id=addition_id,
                               search_result=original_data,
                               )


@check_additions_bp.route('/preview_pdf/<int:addition_id>', methods=['GET'])
@login_required
def preview_pdf(addition_id):
    search_engine = AdditionSearchEngine(db.session, addition_id)
    search_result = search_engine.search_addition()
    try:
        return send_file(search_result.pdf_file_path)
    except FileNotFoundError:
        abort(404)


@check_additions_bp.route('/delete_addition/<int:addition_id>', methods=['DELETE'])
@login_required
def delete_addition(addition_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    addition_manager = AdditionManager(db.session)
    try:
        addition_on_delete = addition_manager.delete_addition(addition_id)
        if addition_on_delete:
            db.session.commit()
            flash("Əlavə uğurla silindi", "success")
            return jsonify({
                'status': 'success',
            }), 200
        else:
            flash("Əlavə silinmədi. Server tərəfində xəta baş verdi", "error")
            db.session.rollback()
            return jsonify({
                'status': 'error',
            }), 500
    except ValueError:
        flash("Ümumi məbləğ mənfi ola bilməz. Bəzi aktları silin", "warning")
        return jsonify({
            'status': 'error',
        }), 500