import flask_wtf
from flask import Blueprint, render_template, request
from forms.contract_search import SearchContract
from database.db_init import db
from database.validators import SearchEngine
from configuration import POSTS_PER_PAGE


def handle_search(search_query: str, form: flask_wtf.Form, page: int, filters: str, order: str) -> render_template:
    search_engine = SearchEngine(db.session, search_query)
    search_results = search_engine.search_query(page, POSTS_PER_PAGE, filters, order)
    total_contracts = search_results["total_contracts"]
    total_results = search_results["results_per_page"]
    print(len(total_results))
    total_pages = (total_contracts // POSTS_PER_PAGE) + (1 if total_contracts % POSTS_PER_PAGE != 0 else 0)
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=total_results,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action="search",
                           search_query=search_query,
                           filters=filters,
                           order=order
                           )


def handle_all_contracts(form: flask_wtf.Form, page: int) -> render_template:
    search_engine = SearchEngine(db.session)
    search_results = search_engine.get_all_results(db, page, POSTS_PER_PAGE)
    total_contracts = search_results["total_contracts"]
    companies = search_results["results_per_page"]
    print(len(companies))
    total_pages = (total_contracts // POSTS_PER_PAGE) + (1 if total_contracts % POSTS_PER_PAGE != 0 else 0)
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=companies,
                           form=form,
                           page=page,
                           total_pages=total_pages,
                           action="all"
                           )


check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    form = SearchContract()
    action = request.args.get("action", "all")
    page = request.args.get("page", 1, type=int)

    match action:
        case "search":
            filters = request.args.get("filters", None)
            order = request.args.get("order", None)
            search_query = request.args.get("search", None)
            return handle_search(search_query, form, page, filters, order)
        case "all":
            return handle_all_contracts(form, page)
    return handle_all_contracts(form, page)


@check_contracts_bp.route('/contract/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    search_engine = SearchEngine(db.session, contract_id)
    search_result = search_engine.search_company()
    return render_template("check_contract.html", search_result=search_result)
