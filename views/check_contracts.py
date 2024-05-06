from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for
from forms.contract_search import SearchContract
from database.models import *
from database.db_init import db
from database.validators import SearchEngine
check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    form = SearchContract()
    search_query = request.args.get("search")
    if search_query:
        search_engine = SearchEngine(search_query, db.session)
        search_results = search_engine.search_voen()
        print(search_results)
        return render_template("check_contracts.html",
                               all_contracts=False,
                               new_contract=True,
                               dashboard=True,
                               companies=search_results,
                               form=form
                               )

    stmt = db.session.query(Companies).join(Contract.company).distinct()
    results = db.session.execute(stmt)
    companies = results.scalars().all()
    return render_template("check_contracts.html",
                           all_contracts=False,
                           new_contract=True,
                           dashboard=True,
                           companies=companies,
                           form=form)