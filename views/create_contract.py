from flask import Blueprint, render_template, redirect, flash, url_for, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import OperationalError, DBAPIError
from forms.create_contract_form import CreateContractForm
from database.models import *
from database.db_init import db
from database.validators import ContractManager
from forms.custom_validators import add_contract_pdf
from forms.filters import *

create_contract_bp = Blueprint('create_contract', __name__)


# Our create_contract routes
@create_contract_bp.route('/create_contract', methods=["GET"])
@login_required
def create_contract():
    if current_user.role == "viewer":
        abort(401)
    categories = ContractManager(db.session).search_categories()
    form = CreateContractForm()
    form.categories.choices = [(category.id, category.category_name) for category in categories]
    return render_template("add_contract.html", form=form)


@create_contract_bp.route('/save_contract', methods=["POST"])
@login_required
def save_contract():
    form = CreateContractForm()
    filtered_company_name = filter_string_fields(form.company.data)
    start_date = form.start_date.data
    end_date = form.end_date.data
    filtered_voen = filter_string(form.voen.data)
    filtered_contract = filter_string(form.contract_number.data)
    contract_manager = ContractManager(db.session)
    categories = contract_manager.search_categories()
    form.categories.choices = [(category.id, category.category_name) for category in categories]
    if form.validate_on_submit():
        selected_category_id = form.categories.data
        valid_category = next((cat for cat in categories if cat.id == selected_category_id), None)
        if valid_category is None:
            flash('Yanlış kateqoriya seçilib. Zəhmət olmasa düzgün seçimi edin', 'error')
            return render_template("add_contract.html", form=form)
        if start_date >= end_date:
            flash('Başlanğıc tarixi bitmə tarixindən sonra və ya ona bərabər ola bilməz', 'warning')
            return render_template('add_contract.html', form=form)
        elif end_date <= start_date:
            flash('Bitmə tarixi orijinal başlanğıc tarixindən əvvəl və ya ona bərabər ola bilməz', 'warning')
            return render_template('add_contract.html', form=form)
        try:
            file = form.pdf_file.data
            filename = secure_filename(file.filename)
            file_path = add_contract_pdf(current_app.config['UPLOAD_FOLDER'], filename, filtered_company_name)
            company = contract_manager.get_or_create_company(filtered_company_name, filtered_voen)
            contract = Contract(
                contract_number=filtered_contract,
                date=form.start_date.data,
                end_date=form.end_date.data,
                amount=float(form.amount.data),
                remained_amount=float(form.amount.data),
                company_id=company.id,
                adv_payer=form.is_adv_payer.data,
                pdf_file_path=file_path,
                category_id=form.categories.data
            )
            db.session.add(contract)
            db.session.commit()
            file.save(file_path)
            flash("Müqavilə uğurla yadda saxlanıldı", "success")
            return redirect(url_for("create_contract.create_contract"))

        except ValueError as e:
            flash(str(e), "warning")
            db.session.rollback()
        except (DBAPIError, OperationalError):
            flash("Xəta baş verdi. əməliyyat bərpa edildi", "error")
            db.session.rollback()
    else:
        flash("Doğrulama xətası. Zəhmət olmasa, bütün sahələri yoxlayın", "error")
    return render_template('add_contract.html', form=form)
