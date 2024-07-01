import flask_wtf
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, send_file
from werkzeug.utils import secure_filename
from forms.contract_search import SearchContract
from forms.filters import *
from forms.edit_contract_form import EditContractForm
from database.db_init import db
from database.validators import SearchEngine, Edit
from configuration import POSTS_PER_PAGE


def handle_search(search_query: str, form: flask_wtf.Form, page: int = None, filters: str = None, order: str = None) -> render_template:
    search_engine = SearchEngine(db.session, search_query)
    search_results = search_engine.search_query(page, POSTS_PER_PAGE, filters, order)
    total_contracts = search_results["total_contracts"]
    total_results = search_results["results_per_page"]
    total_pages = (total_contracts // POSTS_PER_PAGE) + (1 if total_contracts % POSTS_PER_PAGE != 0 else 0)

    if page > total_pages:
        return redirect(
            url_for('all_contracts.get_all_contracts', action="search", page=total_pages, filters=filters, orders=order,
                    search=search_query))
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=total_results,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action=session["contract_action"],
                           search_query=search_query,
                           filters=filters,
                           order=order,
                           posts_per_page=POSTS_PER_PAGE
                           )


def handle_all_contracts(form: flask_wtf.Form, page: int) -> render_template:
    search_engine = SearchEngine(db.session)
    search_results = search_engine.get_all_results(db, page, POSTS_PER_PAGE)
    total_contracts = search_results["total_contracts"]
    companies = search_results["results_per_page"]
    total_pages = (total_contracts // POSTS_PER_PAGE) + (1 if total_contracts % POSTS_PER_PAGE != 0 else 0)
    if page > total_pages:
        return redirect(url_for('all_contracts.get_all_contracts', action="all", page=total_pages))
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=companies,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action=session["contract_action"],
                           posts_per_page=POSTS_PER_PAGE
                           )


check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    form = SearchContract()
    action = request.args.get("action")
    session["contract_action"] = action
    session["which_page"] = "contracts"
    page = request.args.get("page", 1, type=int)
    session["contract_page"] = page
    match action:
        case "search":
            filters = request.args.get("filters", "")
            orders = request.args.get("orders", "")
            session["contract_filters"] = filters
            session["contract_order"] = orders
            search_query = request.args.get("search", "").strip()
            session["contract_search_query"] = search_query
            return handle_search(search_query, form, page, filters, orders)
        case "all":
            return handle_all_contracts(form, page)
    return handle_all_contracts(form, page)


@check_contracts_bp.route('/contract/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    form = EditContractForm()
    search_engine = SearchEngine(db.session, contract_id)
    search_result = search_engine.search_company()
    return render_template("check_contract.html",
                           search_result=search_result,
                           contract_id=contract_id,
                           form=form)


@check_contracts_bp.route('/update_contract/<int:contract_id>', methods=['POST'])
def update_contract(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    edit_engine = Edit(db.session, contract_id)
    original_data = search_engine.search_company()
    form = EditContractForm()
    if form.validate_on_submit():
        file = form.pdf_file.data
        filename = ""
        if file:
            filename = secure_filename(make_unique(f"{original_data.company.voen}_{file.filename}"))
        data_dict = dict(
            contract_number=filter_contract_number(
                form.contract_number.data) if form.contract_number.data else original_data.contract_number,
            date=form.date.data if form.date.data else original_data.date,
            amount=float(form.amount.data) if form.amount.data else original_data.amount,
            pdf_file_path=filename if form.pdf_file.data else original_data.pdf_file_path,
            company_name=filter_string_fields(
                form.company.data) if form.company.data else original_data.company.company_name,
            voen=filter_voen(form.voen.data) if form.voen.data else original_data.company.voen,
        )
        success, message = edit_engine.update_data(data_dict, form.pdf_file.data)
        if success:
            db.session.commit()
            flash(message, "success")
            return jsonify(redirect_url=url_for('all_contracts.get_contract', contract_id=contract_id))
        else:
            db.session.rollback()
            flash(message, "warning")
            return jsonify(redirect_url=url_for('all_contracts.get_contract', contract_id=contract_id))
        # return redirect(url_for('all_contracts.get_contract', contract_id=contract_id))
    else:
        errors = {field.name: field.errors for field in form}
        return jsonify(errors=errors, success=False)


@check_contracts_bp.route('/preview_pdf/<int:contract_id>', methods=['GET'])
def preview_pdf(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    contract_result = search_engine.search_company()
    if contract_result and contract_result.pdf_file_path:
        return send_file(contract_result.pdf_file_path)
    else:
        return jsonify({"error": "Company not found"}), 404


@check_contracts_bp.route('/related_contracts/<string:voen>', methods=['GET'])
def related_contracts(voen):
    form = SearchContract()
    session["which_page"] = "companies"
    session["company_voen"] = voen
    page = request.args.get("page", 1, type=int)
    session["contract_action"] = "company_search"
    print(session["contract_action"])
    session["contract_search_query"] = voen
    search_query = voen
    return handle_search(search_query, form, page=page)
