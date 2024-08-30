from flask import Blueprint, render_template, redirect, flash, url_for, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError, NoResultFound, DBAPIError
from forms.create_addition_form import CreateAddition
from database.validators import AdditionManager, AdditionSearchEngine
from database.db_init import db
from forms.custom_validators import add_contract_pdf
from forms.filters import filter_act_number

create_addition_bp = Blueprint('create_addition', __name__)


# Our create act routes
@create_addition_bp.route('/create_addition', methods=['GET'])
@login_required
def create_addition():
    if current_user.role == "viewer":
        abort(401)
    form = CreateAddition()
    return render_template('create_addition.html', form=form)


@create_addition_bp.route('/save_addition', methods=['GET', 'POST'])
@login_required
def save_addition():
    if current_user.role == "viewer":
        abort(401)
    form = CreateAddition()
    filtered_addition_number = filter_act_number(form.addition_number.data)
    act_manager = AdditionManager(db.session)
    search_engine = AdditionSearchEngine(db.session)
    if form.validate():
        try:
            search_engine.increase_amount(form.contract_id.data, form.addition_amount.data)
        except NoResultFound:
            abort(404)
        except (DBAPIError, OperationalError):
            flash("Something went wrong in the database", "error")
            return render_template('create_addition.html', form=form)
        try:
            file = form.pdf_file_act.data
            filename = secure_filename(file.filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER_ADDITIONS'], filename)
            addition_info = dict(
                addition_number=filtered_addition_number,
                pdf_file_path=file_path,
                date=form.addition_date.data,
                amount=form.addition_amount.data,
                contract_id=form.contract_id.data
            )
            act_manager.create_addition(addition_info)
            file.save(file_path)
            flash("The addition is saved successfully!", "success")
            db.session.commit()
            return redirect(url_for('create_addition.create_addition'))

        except OperationalError:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
            return render_template('create_addition.html', form=form)
    else:
        flash("Validation Error. Please check all fields", "error")
    return render_template('create_addition.html', form=form)
