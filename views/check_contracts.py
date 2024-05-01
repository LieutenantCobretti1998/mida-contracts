from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for
from sqlalchemy.orm import selectinload, join
from sqlalchemy import select
from database.models import *
from database.db_init import db

check_contracts_bp = Blueprint('all_contracts', __name__)


@check_contracts_bp.route('/all_contracts', methods=['GET'])
def get_all_contracts():
    stmt = db.session.query(Companies).join(Contract.company).distinct()
    print(stmt)
    results = db.session.execute(stmt)
    companies = results.scalars().all()

    # stmt = select(Companies).join(VOEN, Companies.id == VOEN.company_id).join(Contract, VOEN.id == Contract.voen_id)
    # results = db.session.execute(stmt)
    # companies = results.scalars().all()
    return render_template("check_contracts.html",
                           all_contracts=False,
                           new_contract=True,
                           dashboard=True,
                           companies=companies)