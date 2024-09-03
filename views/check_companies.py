from flask import Blueprint, render_template, url_for, jsonify, flash, abort, redirect
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from database.helpers import create_new_token
from database.models import ContractUpdateToken
from forms.edit_company_form import EditCompanyForm
from forms.filters import *
from database.db_init import db
from database.validators import CompanySearchEngine, EditCompany, SearchEngine, CompanyManager


check_companies_bp = Blueprint('all_companies', __name__)


@check_companies_bp.route('/all_companies', methods=['GET'])
@login_required
def get_all_companies():
    return render_template("check_companies.html")


@check_companies_bp.route('/company_overview/<int:company_id>', methods=['GET'])
@login_required
def get_company(company_id):
    try:
        search_engine = CompanySearchEngine(db.session, company_id)
        search_result = search_engine.search_company()
        return render_template("check_company.html",
                               search_result=search_result,
                               company_id=company_id
                               )
    except NoResultFound:
        abort(404)


@check_companies_bp.route('/company/<int:company_id>', methods=['GET'])
@login_required
def edit_company(company_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    form = EditCompanyForm()
    try:
        search_engine = CompanySearchEngine(db.session, company_id)
        search_result = search_engine.search_company()
        existing_token = db.session.query(ContractUpdateToken).filter_by(company_id=company_id,
                                                                         user_id=current_user.id).first()
        if existing_token is not None:
            if existing_token.is_expired():
                db.session.delete(existing_token)
                db.session.commit()
                token = create_new_token(company_id=company_id, user_id=current_user.id)
            else:
                token = existing_token.token
        else:
            token = create_new_token(company_id=company_id, user_id=current_user.id)
        return render_template("edit_company.html",
                               search_result=search_result,
                               form=form,
                               token=token
                               )
    except NoResultFound:
        abort(404)


@check_companies_bp.route('/update_company/<string:company_token>', methods=['POST'])
@login_required
def update_company(company_token):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    used_token = db.session.query(ContractUpdateToken).filter_by(token=company_token).first()
    if used_token is None:
        abort(404)
    company_id = used_token.company_id
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
            db.session.delete(used_token)
            db.session.commit()
            flash(message, "success")
            return redirect(url_for('all_companies.get_company', company_id=company_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return render_template("edit_company.html", form=form, company_id=company_id,
                                   search_result=original_data,
                                   token=company_token)
    else:
        flash("Validation Error. Please check all fields", "error")
        return render_template("edit_company.html", form=form, company_id=company_id,
                               search_result=original_data,
                               token=company_token)


@check_companies_bp.route('/delete_company/<int:company_id>', methods=['DELETE'])
@login_required
def delete_company(company_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
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
