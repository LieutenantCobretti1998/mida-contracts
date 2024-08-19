from flask import Blueprint, render_template, redirect, flash, url_for, abort, send_file, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.exc import NoResultFound, DBAPIError, OperationalError
from database.validators import ActsSearchEngine, EditAct, ActsManager
from database.db_init import db
from forms.custom_validators import check_amount, check_act_amount_difference, calculate_amount
from forms.edit_act_form import EditActForm
from forms.filters import *

check_acts_bp = Blueprint('all_acts', __name__)


# Our roots for acts
@check_acts_bp.route('/act_overview/<int:act_id>', methods=['GET'])
def get_act(act_id):
    try:
        search_engine = ActsSearchEngine(db.session, act_id)
        search_result = search_engine.search_act()
        return render_template("check_act.html",
                               search_result=search_result,
                               act_id=act_id
                               )
    except NoResultFound:
        abort(404)


@check_acts_bp.route('/act/<int:act_id>', methods=['GET'])
def edit_act(act_id):
    try:
        form = EditActForm()
        search_engine = ActsSearchEngine(db.session, act_id)
        search_result = search_engine.search_act()
        return render_template("edit_act.html",
                               search_result=search_result,
                               act_id=act_id,
                               form=form)
    except NoResultFound:
        abort(404)


@check_acts_bp.route('/update_act/<int:act_id>', methods=['POST'])
def update_act(act_id):
    search_engine = ActsSearchEngine(db.session, act_id)
    edit_engine = EditAct(db.session, act_id)
    original_data = search_engine.search_act()
    form = EditActForm()

    if form.validate_on_submit():
        try:
            difference = check_act_amount_difference(form.act_amount.data, original_data.amount)
            check_amount(form.act_amount.data, original_data.amount)
            search_engine.decrease_or_increase_difference_amount(form.contract_id.data, difference)
        except NoResultFound:
            abort(404)
        except (DBAPIError, OperationalError):
            flash("Something went wrong in the database", "error")
            return render_template('edit_act.html', form=form, act_id=act_id, search_result=original_data)
        except ValueError:
            flash("Act's amount is bigger than the total contract's amount. Please check act amount field", "warning")
            return render_template('edit_act.html', form=form, act_id=act_id, search_result=original_data)
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
            return redirect(url_for('all_acts.get_act', act_id=act_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return redirect(url_for('all_acts.edit_act', act_id=act_id))
    else:
        flash("Validation Error. Please check all fields", "error")
        return render_template('edit_act.html', form=form, act_id=act_id, search_result=original_data)


@check_acts_bp.route('/preview_pdf/<int:act_id>', methods=['GET'])
def preview_pdf(act_id):
    search_engine = ActsSearchEngine(db.session, act_id)
    search_result = search_engine.search_act()
    try:
        return send_file(search_result.pdf_file_path)
    except FileNotFoundError:
        abort(404)


@check_acts_bp.route('/delete_act/<int:act_id>', methods=['DELETE'])
def delete_act(act_id):
    act_manager = ActsManager(db.session)
    act_on_delete = act_manager.delete_act(act_id)
    if act_on_delete:
        db.session.commit()
        flash("Act deleted successfully", "success")
        return jsonify({
            'status': 'success',
        }), 200
    else:
        flash("Could not delete the contract. Something went wrong on the server side. Maybe data is outdated", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500