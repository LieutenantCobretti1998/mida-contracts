import flask_wtf
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, send_file
from forms.edit_company_form import EditCompanyForm
from forms.filters import *
from forms.company_search import CompanySearchForm
from database.db_init import db
from database.validators import CompanySearchEngine
from configuration import POSTS_PER_PAGE


def handle_search(search_query: str, form: flask_wtf.Form, page: int, filters: str, order: str) -> render_template:
    search_engine = CompanySearchEngine(db.session, search_query)
    search_results = search_engine.search_query(page, POSTS_PER_PAGE, filters, order)
    total_companies = search_results["total_companies"]
    total_results = search_results["results_per_page"]
    total_pages = (total_companies // POSTS_PER_PAGE) + (1 if total_companies % POSTS_PER_PAGE != 0 else 0)
    if page > total_pages:
        return redirect(
            url_for('all_companies.get_all_companies', action="search", page=total_pages, filters=filters, orders=order,
                    search=search_query))
    return render_template("check_companies.html",
                           amount_of_companies=total_companies,
                           companies=total_results,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action=session["company_action"],
                           search_query=search_query,
                           filters=filters,
                           order=order,
                           posts_per_page=POSTS_PER_PAGE
                           )


def handle_all_companies(form: flask_wtf.Form, page: int) -> render_template:
    search_engine = CompanySearchEngine(db.session)
    search_results = search_engine.get_all_results(page, POSTS_PER_PAGE)
    print(search_results)
    total_companies = search_results["total_companies"]
    companies = search_results["results_per_page"]
    total_pages = (total_companies // POSTS_PER_PAGE) + (1 if total_companies % POSTS_PER_PAGE != 0 else 0)
    if page > total_pages:
        return redirect(url_for('all_companies.get_all_companies', action="all", page=total_pages))
    return render_template("check_companies.html",
                           amount_of_companies=total_companies,
                           companies=companies,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action=session["company_action"],
                           posts_per_page=POSTS_PER_PAGE
                           )


check_companies_bp = Blueprint('all_companies', __name__)


@check_companies_bp.route('/all_companies', methods=['GET'])
def get_all_companies():
    form = CompanySearchForm()
    action = request.args.get('action', None, type=str)
    session["company_action"] = action
    page = request.args.get("page", 1, type=int)
    session["company_page"] = page
    match action:
        case "search":
            filters = request.args.get("filters", "")
            orders = request.args.get("orders", "")
            session["company_filters"] = filters
            session["company_order"] = orders
            search_query = request.args.get("search", "").strip()
            session["company_search_query"] = search_query
            return handle_search(search_query, form, page, filters, orders)
        case "all":
            return handle_all_companies(form, page)
    return handle_all_companies(form, page)


@check_companies_bp.route('/company/<int:company_id>', methods=['GET', 'POST'])
def get_company(company_id):
    form = EditCompanyForm()
    search_engine = CompanySearchEngine(db.session, company_id)
    search_result = search_engine.search_company()
    return render_template("check_company.html",
                           search_result=search_result,
                           form=form
                           )
