import flask_wtf
from flask import Blueprint, render_template, request, session, url_for, jsonify, flash
from forms.edit_company_form import EditCompanyForm
from forms.filters import *
from forms.company_search import CompanySearchForm
from database.db_init import db
from database.validators import CompanySearchEngine, EditCompany, SearchEngine, CompanyManager


check_companies_bp = Blueprint('all_companies', __name__)


@check_companies_bp.route('/all_companies', methods=['GET'])
def get_all_companies():
    return render_template("check_companies.html")


@check_companies_bp.route('/company/<int:company_id>', methods=['GET', 'POST'])
def get_company(company_id):
    form = EditCompanyForm()
    search_engine = CompanySearchEngine(db.session, company_id)
    search_result = search_engine.search_company()
    return render_template("check_company.html",
                           search_result=search_result,
                           form=form
                           )


@check_companies_bp.route('/update_company/<int:company_id>', methods=['POST'])
def update_company(company_id):
    search_engine = SearchEngine(db.session, company_id)
    edit_engine = EditCompany(db.session, company_id)
    original_data = search_engine.search_company()
    form = EditCompanyForm()
    if form.validate_on_submit():
        data_dict = dict(
            company_name=filter_string_fields(form.company.data) if form.company.data else original_data.company_name,
            voen=filter_voen(form.voen.data) if form.voen.data else original_data.voen,
            bank_name=form.bank_name.data if form.bank_name.data else original_data.bank_name,
            m_h=form.m_h.data if form.m_h.data else original_data.m_h,
            h_h=form.h_h.data if form.h_h.data else original_data.h_h,
            swift=form.swift.data if form.swift.data else original_data.swift,
            email=form.email.data if form.email.data else original_data.email,
            telephone_number=form.telephone_number.data if form.telephone_number.data else original_data.telephone_number,
            address=form.address.data if form.address.data else original_data.address,
            website=form.website.data if form.website.data else original_data.website
        )
        success, message = edit_engine.update_data(data_dict)
        if success:
            flash(message, "success")
            return jsonify(redirect_url=url_for('all_companies.get_company', company_id=company_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return jsonify(redirect_url=url_for('all_companies.get_company', company_id=company_id))
    else:
        errors = {field.name: field.errors for field in form}
        return jsonify(errors=errors)


@check_companies_bp.route('/delete_company/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    print(company_id)
    company_manager = CompanyManager(db.session)
    company_on_delete = company_manager.delete_company(company_id)
    if company_on_delete:
        db.session.commit()
        flash("Company deleted successfully", "success")
        return jsonify({
            'status': 'success',
        }), 200
    else:
        db.session.rollback()
        flash("Could not delete the company. Something went wrong on the server side", "error")
        return jsonify({
            'status': 'error',
        }), 500
