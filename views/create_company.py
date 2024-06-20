from flask import Blueprint, render_template, redirect, url_for, jsonify, flash
from sqlalchemy.exc import OperationalError

from database.db_init import db
from database.models import Companies
from database.validators import CompanyManager
from forms.create_company import CompanyForm
from forms.filters import filter_string_fields, filter_voen

create_company_bp = Blueprint("create_company", __name__)


@create_company_bp.route("/create_company", methods=["GET", "POST"])
def create_company():
    form = CompanyForm()
    return render_template("create_company.html", form=form)


@create_company_bp.route("/save_company", methods=["POST"])
def save_company():
    form = CompanyForm()
    company_manager = CompanyManager(db.session)
    filtered_company_name = filter_string_fields(form.company.data)
    filtered_voen = filter_voen(form.voen.data)
    if form.validate():

        try:
            company = company_manager.get_or_create_company(filtered_company_name, filtered_voen)
            company_manager.check_swift(form.company.data)
            company_row = Companies(
                company_name=company.company_name,
                voen=company.voen,
                bank_name=form.bank_name.data,
                m_h=form.m_h.data,
                h_h=form.h_h.data,
                swift=form.swift.data,
                email=form.email.data,
                telephone_number=form.telephone_number.data,
                address=form.address.data,
                website=form.website.data
            )
            db.session.add(company_row)
            db.session.commit()
            flash("The contract is saved successfully!", "success")
            return redirect(url_for("create_company.create_company"))
        except ValueError as e:
            flash(str(e), "warning")
        except OperationalError:
            flash("Something went wrong. transaction was restored", "error")
            db.session.rollback()
    else:
        flash("Validation Error. Please check all fields", "error")
    return render_template("create_company.html", form=form)
