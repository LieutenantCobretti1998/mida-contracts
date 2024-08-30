from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import OperationalError
from database.db_init import db
from database.validators import CompanyManager
from forms.create_company import CompanyForm
from forms.filters import filter_string_fields, filter_voen

create_company_bp = Blueprint("create_company", __name__)


@create_company_bp.route("/create_company", methods=["GET"])
@login_required
def create_company():
    if current_user.role == "viewer":
        abort(401)
    form = CompanyForm()
    return render_template("create_company.html", form=form)


@create_company_bp.route("/save_company", methods=["POST"])
@login_required
def save_company():
    if current_user.role == "viewer":
        abort(401)
    form = CompanyForm()
    company_manager = CompanyManager(db.session)
    filtered_company_name = filter_string_fields(form.company.data)
    filtered_voen = filter_voen(form.voen.data)
    company_data = dict(
        bank_name=form.bank_name.data if form.bank_name.data else None,
        m_h=form.m_h.data if form.m_h.data else None,
        h_h=form.h_h.data if form.h_h.data else None,
        swift=form.swift.data if form.swift.data else None,
        email=form.email.data if form.email.data else None,
        telephone_number=form.telephone_number.data if form.telephone_number.data else None,
        address=form.address.data if form.address.data else None,
        website=form.website.data if form.website.data else None
    )
    if form.validate():
        try:
            company_manager.check_swift(form.swift.data)
            company_manager.get_or_create_company(filtered_company_name, filtered_voen, company_data)
            db.session.commit()
            flash("The company requisites is saved successfully!", "success")
            return redirect(url_for("create_company.create_company"))
        except ValueError as e:
            flash(str(e), "warning")
            db.session.rollback()
        except OperationalError:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
    else:
        flash("Validation Error. Please check all fields", "error")
        db.session.rollback()
    return render_template("create_company.html", form=form)
