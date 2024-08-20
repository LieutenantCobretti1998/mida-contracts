from flask import Blueprint, render_template, redirect, flash, url_for, abort, send_file, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.exc import NoResultFound, DBAPIError, OperationalError
from database.validators import ActsSearchEngine, EditAct, AdditionManager, AdditionSearchEngine
from database.db_init import db
from forms.custom_validators import check_amount, check_act_amount_difference, calculate_amount
from forms.edit_act_form import EditActForm
from forms.edit_addition import EditAdditionForm
from forms.filters import *

check_additions_bp = Blueprint('all_additions', __name__)


# Our roots for acts
@check_additions_bp.route('/act_addition/<int:addition_id>', methods=['GET'])
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
def edit_addition(addition_id):
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
def update_addition(addition_id):
    search_engine = AdditionSearchEngine(db.session, addition_id)
    edit_engine = EditAct(db.session, addition_id)
    original_data = search_engine.search_act()
    form = EditActForm()

    if form.validate_on_submit():
        if form.act_amount.data:
            try:
                difference = check_act_amount_difference(form.act_amount.data, original_data.amount)
                check_amount(form.act_amount.data, original_data.amount)
                search_engine.decrease_or_increase_difference_amount(form.contract_id.data, difference)
            except NoResultFound:
                abort(404)
            except (DBAPIError, OperationalError):
                flash("Something went wrong in the database", "error")
                return render_template('edit_act.html', form=form, act_id=addition_id, search_result=original_data)
            except ValueError:
                flash("Act's amount is bigger than the total contract's amount. Please check act amount field", "warning")
                return render_template('edit_act.html', form=form, act_id=addition_id, search_result=original_data)
        file = form.pdf_file_act.data
        filename = ""
        if file:
            filename = secure_filename(make_unique(f"{file.filename}"))
        data_dict = dict(
            act_number=filter_act_number(form.act_number.data) if form.act_number.data else original_data.act_number,
            pdf_file_path=filename if file else None,
            date=form.act_date.data if form.act_date.data else original_data.date,
            amount=form.act_amount.data if form.act_amount.data else original_data.amount,
            contract_id=form.contract_id.data if form.contract_id.data else original_data.contract_id,
        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file_act.data)
        if success:
            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_acts.get_act', act_id=addition_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return redirect(url_for('all_acts.edit_act', act_id=addition_id))
    else:
        flash("Validation Error. Please check all fields", "error")
        return render_template('edit_act.html', form=form, act_id=addition_id, search_result=original_data)


@check_additions_bp.route('/preview_pdf/<int:addition_id>', methods=['GET'])
def preview_pdf(addition_id):
    search_engine = AdditionSearchEngine(db.session, addition_id)
    search_result = search_engine.search_addition()
    try:
        return send_file(search_result.pdf_file_path)
    except FileNotFoundError:
        abort(404)


@check_additions_bp.route('/delete_addition/<int:addition_id>', methods=['DELETE'])
def delete_addition(addition_id):
    addition_manager = AdditionManager(db.session)
    addition_on_delete = addition_manager.delete_addition(addition_id)
    if addition_on_delete:
        db.session.commit()
        flash("Addition deleted successfully", "success")
        return jsonify({
            'status': 'success',
        }), 200
    else:
        flash("Could not delete the addition. Something went wrong on the server side. Maybe data is outdated", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500