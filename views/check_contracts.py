import flask_wtf
from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for
from forms.contract_search import SearchContract
from database.models import *
from database.db_init import db
from database.validators import SearchEngine


def handle_search(search_query: str, form: flask_wtf.Form) -> render_template:
    search_engine = SearchEngine(search_query, db.session)
    search_results = search_engine.search_voen()
    total_contracts = sum(len(company.contracts) for company in search_results)
    print("voen")
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=search_results,
                           form=form
                           )


def handle_all_contracts(form: flask_wtf.Form) -> render_template:
    stmt = db.session.query(Companies).join(Contract.company).distinct()
    results = db.session.execute(stmt)
    companies = results.scalars().all()
    total_contracts = sum(len(company.contracts) for company in companies)
    print("all")
    return render_template("check_contracts.html",
                           amount_of_companies=total_contracts,
                           companies=companies,
                           form=form
                           )


check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    print(request.args)
    form = SearchContract()
    action = request.args.get("action", "all")
    search_query = request.args.get("search", None)

    match action:
        case "search":
            return handle_search(search_query, form)
        case "all":
            return handle_all_contracts(form)
    return handle_all_contracts(form)
