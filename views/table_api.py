from flask import Blueprint, jsonify, request
from database.db_init import db
from database.models import *
from database.validators import SearchEngine, CompanySearchEngine

api_contracts_bp = Blueprint('api_contracts', __name__)
api_companies_bp = Blueprint('api_companies', __name__)
# Dictionary of tuples
column_map_contracts = {
    "Company Name": ("company_name", Companies),
    "Voen": ("voen", Companies),
    "Contract Number": ("contract_number", Contract),
    "Date": ("date", Contract),
    "Amount": ("amount", Contract),
    "Adv Payer": ("adv_payer", Contract)
}

column_map_companies = {
    "Company Name": ("company_name", Companies),
    "Voen": ("voen", Companies),
    "Related Contracts": ("related_contracts", None)
}


@api_contracts_bp.route('/all_contracts', methods=['GET'])
def all_contracts_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_contracts.get(order_by, ("id", Contract))
    search_engine = SearchEngine(db.session)
    contract_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": contract_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_contracts_bp.route('/all_contracts/<string:search>', methods=['GET'])
def get_search(search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_contracts.get(order_by, ("id", Contract))
    search_engine = SearchEngine(db.session, search)
    contract_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": contract_list,
        "total_count": total_count
    }
    return jsonify(response)


# Here now we will have our company's api for the table

@api_companies_bp.route('/all_companies', methods=['GET'])
def all_companies_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_companies.get(order_by, ("id", Companies))
    search_engine = CompanySearchEngine(db.session)
    company_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": company_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_companies_bp.route('/all_companies/<string:search>', methods=['GET'])
def get_search(search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_companies.get(order_by, ("id", Companies))
    search_engine = CompanySearchEngine(db.session, search)
    company_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": company_list,
        "total_count": total_count
    }
    return jsonify(response)