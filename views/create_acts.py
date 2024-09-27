from flask import Blueprint, render_template, redirect, flash, url_for, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError, NoResultFound, DBAPIError
from forms.create_act_form import CreateAct
from database.validators import ActsManager, ActsSearchEngine
from database.db_init import db
from forms.custom_validators import add_contract_pdf, check_amount
from forms.filters import filter_act_number

create_act_bp = Blueprint('create_act', __name__)


# Our create act routes
@create_act_bp.route('/create_act', methods=['GET', 'POST'])
@login_required
def create_act():
    if current_user.role == "viewer":
        abort(401)
    form = CreateAct()
    return render_template('create_act.html', form=form)


@create_act_bp.route('/save_act', methods=['POST'])
@login_required
def save_act():
    if current_user.role == "viewer":
        abort(401)
    form = CreateAct()
    filtered_act_number = filter_act_number(form.act_number.data)
    act_manager = ActsManager(db.session)
    search_engine = ActsSearchEngine(db.session)
    if form.validate():
        try:
            total_amount = search_engine.search_related_contract_amount(form.contract_id.data)
            remained_amount = check_amount(form.act_amount.data, total_amount)
            search_engine.decrease_amount(form.contract_id.data, remained_amount)

        except NoResultFound:
            abort(404)
        except (DBAPIError, OperationalError):
            flash("Verilənlər bazasında xəta baş verdi", "error")
            return render_template('create_act.html', form=form)

        except ValueError:
            flash("Aktın məbləği müqavilənin ümumi məbləğindən böyükdür. Zəhmət olmasa akt məbləği sahəsini yoxlayın", "warning")
            return render_template('create_act.html', form=form)
        try:
            file = form.pdf_file_act.data
            filename = secure_filename(file.filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER_ACTS'], filename)
            act_info = dict(
                act_number=filter_act_number(filtered_act_number),
                pdf_file_path=file_path,
                date=form.act_date.data,
                amount=form.act_amount.data,
                contract_id=form.contract_id.data
            )
            act_manager.create_act(act_info)
            file.save(file_path)
            flash("Akt uğurla saxlanıldı!", "success")
            db.session.commit()
            return redirect(url_for('create_act.create_act'))

        except (OperationalError, DBAPIError):
            flash("Xəta baş verdi. əməliyyat bərpa edildi", "error")
            db.session.rollback()
            return render_template('create_act.html', form=form)
    else:
        flash("Doğrulama Xətası. Bütün sahələri yoxlayın", "error")
    return render_template('create_act.html', form=form)

