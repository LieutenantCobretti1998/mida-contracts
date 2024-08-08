from flask import Blueprint, render_template, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError
from forms.create_act_form import CreateAct
from database.validators import ActsManager
from database.db_init import db
from forms.custom_validators import add_contract_pdf
from forms.filters import filter_act_number

create_act_bp = Blueprint('create_act', __name__)


# Our create act routes
@create_act_bp.route('/create_act', methods=['GET', 'POST'])
def create_act():
    form = CreateAct()
    return render_template('create_act.html', form=form)


@create_act_bp.route('/save_act', methods=['GET', 'POST'])
def save_act():
    form = CreateAct()
    filtered_act_number = filter_act_number(form.act_number.data)
    act_manager = ActsManager(db.session)
    if form.validate():
        try:
            file = form.pdf_file_act.data
            filename = secure_filename(file.filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER_ACTS'], filtered_act_number, filename)
            act_info = dict(
                act_number=filtered_act_number,
                pdf_file_path=file_path,
                date=form.act_date.data,
                amount=form.act_amount.data,
                contract_id=form.contract_id.data
            )
            act_manager.create_act(act_info)
            file.save(file_path)
            flash("The act is saved successfully!", "success")
            return redirect(url_for('create_act.create_act'))

        except OperationalError:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
            return render_template('create_act.html', form=form)
    else:
        flash("Validation Error. Please check all fields", "error")
    return render_template('add_contract.html', form=form)