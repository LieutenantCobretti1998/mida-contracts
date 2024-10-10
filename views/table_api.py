from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from database.db_init import db
from database.models import *
from database.validators import (SearchEngine, CompanySearchEngine, ActsSearchEngine, CategoriesManager,
                                 CategoriesSearchEngine, EditCategory, AdditionSearchEngine, DashBoard,
                                 UserSearchEngine)

api_contracts_bp = Blueprint('api_contracts', __name__)
api_companies_bp = Blueprint('api_companies', __name__)
api_acts_bp = Blueprint('api_acts', __name__)
api_categories_bp = Blueprint('api_categories', __name__)
api_additions_bp = Blueprint('api_additions', __name__)
api_dashboard_bp = Blueprint('api_dashboard', __name__)
api_users_bp = Blueprint('api_users', __name__)
# Dictionary of tuples
column_map_contracts = {
    "Company Name": ("company_name", Companies),
    "Voen": ("voen", Companies),
    "Contract Number": ("contract_number", Contract),
    "Start Date": ("date", Contract),
    "End Date": ("end_date", Contract),
    "Amount": ("amount", Contract),
    "Remained Amount": ("remained_amount", Contract),
    "Adv Payer": ("adv_payer", Contract),
    "Category": ("category_id", Contract),
}

column_map_companies = {
    "Company Name": ("company_name", Companies),
    "Voen": ("voen", Companies),
    "Related Contracts": ("related_contracts", None)
}

column_map_acts = {
    "Act Number": ("act_number", Acts),
    "Act Amount": ("amount", Acts),
    "Date": ("date", Acts),
}

column_map_additions = {
    "Addition Number": ("addition_number", Additions),
    "Addition Amount": ("amount", Additions),
    "Date": ("date", Additions),
}

column_map_categories = {
    "Category": ("category_name", Category)
}

column_map_users = {
    "User Name": ("username", User),
    "Role": ("role", User)
}


@api_contracts_bp.route('/all_contracts', methods=['GET'])
@login_required
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
@login_required
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


@api_contracts_bp.route('/all_contracts/related_contract/<string:search>/<int:act_id>', methods=['GET'])
@login_required
def get_search_for_act_contract_edit_mode(search, act_id):
    search_engine = CompanySearchEngine(db.session, search)
    response = search_engine.search_related_contract_api(act_id)
    return jsonify(response)

@api_contracts_bp.route('/all_contracts/related_contract/<string:search>', methods=['GET'])
@login_required
def get_search_for_act_contract(search):
    search_engine = CompanySearchEngine(db.session, search)
    response = search_engine.search_related_contract_api()
    return jsonify(response)

@api_contracts_bp.route('/all_contracts/<int:contract_id>/acts/count', methods=['GET'])
@login_required
def get_count_for_act_contract(contract_id):
    search_engine = CompanySearchEngine(db.session)
    response = search_engine.is_only_act_api(contract_id)

    return jsonify({"count": response})

# Here now we will have our company's api for the table

@api_companies_bp.route('/all_companies', methods=['GET'])
@login_required
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
@login_required
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


@api_companies_bp.route('/all_companies/related_companies/<string:search>', methods=['GET'])
@login_required
def get_search_for_act_companies(search):
    search_engine = CompanySearchEngine(db.session, search)
    response = search_engine.search_related_companies_api()
    return jsonify(response)


@api_companies_bp.route('/all_companies/related_contracts/<string:search>', methods=['GET'])
@login_required
def get_search_for_act_contracts(search):
    search_engine = CompanySearchEngine(db.session, search)
    response = search_engine.search_related_contracts_api()
    return jsonify(response)


# Acts api routes
@api_acts_bp.route('/related_acts/<int:contract_id>', methods=['GET'])
@login_required
def get_related_acts(contract_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_acts.get(order_by, ("id", Acts))
    search_engine = ActsSearchEngine(db.session, contract_id=contract_id)
    act_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": act_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_acts_bp.route('/related_acts/<int:contract_id>/<string:search>', methods=['GET'])
@login_required
def get_search_related_acts(contract_id, search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_acts.get(order_by, ("id", Acts))
    search_engine = ActsSearchEngine(db.session, contract_id=contract_id, search=search)
    acts_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": acts_list,
        "total_count": total_count
    }
    return jsonify(response)


# Additions
@api_additions_bp.route('/related_additions/<int:contract_id>', methods=['GET'])
@login_required
def get_related_additions(contract_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_additions.get(order_by, ("id", Additions))
    search_engine = AdditionSearchEngine(db.session, contract_id=contract_id)
    addition_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": addition_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_acts_bp.route('/related_additions/<int:contract_id>/<string:search>', methods=['GET'])
@login_required
def get_search_related_additions(contract_id, search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_additions.get(order_by, ("id", Additions))
    search_engine = AdditionSearchEngine(db.session, contract_id=contract_id, search=search)
    addition_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": addition_list,
        "total_count": total_count
    }
    return jsonify(response)


# Categories
@api_categories_bp.route('/all_categories', methods=['GET'])
@login_required
def categories():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_categories.get(order_by, ("id", Category))
    search_engine = CategoriesSearchEngine(db.session)
    category_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": category_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_categories_bp.route('/all_categories/add_category', methods=['POST'])
@login_required
def add_category():
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    new_category = request.json
    categories_manager = CategoriesManager(db.session)

    try:
        categories_manager.add_category(new_category.get("category"))
        # Return a success response if the category was added successfully
        return jsonify({
            "message": "Category added successfully!"
        }), 200

    except SQLAlchemyError:
        # Log the exception if needed
        # Return an error response if something went wrong
        return jsonify({
            "message": "An error occurred while adding the category. Something wrong with the database"
        }), 500


@api_categories_bp.route('/all_categories/remove_category/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    categories_manager = CategoriesManager(db.session)
    try:
        categories_manager.delete_category(category_id)
        return jsonify({
            "status": "success",
            "message": "Category deleted successfully!"
        }), 200
    except SQLAlchemyError:
        return jsonify({
            "message": "An error occurred while deleting category. Something wrong with the database"
        }), 500


@api_categories_bp.route('/all_categories/<string:search>', methods=['GET'])
@login_required
def get_search_for_categories(search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'Date')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_categories.get(order_by, ("id", Category))
    search_engine = CategoriesSearchEngine(db.session, search)
    category_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": category_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_categories_bp.route('/all_categories/update_category', methods=['PUT'])
@login_required
def update_category():
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    category_to_update = request.json.get('category_name')
    category_id = request.json.get("id")
    if len(category_to_update) > 30:
        return jsonify({
            "message": "Category is too long. Dont play with front validation:)"
        }), 400
    categories_manager = EditCategory(db.session, category_id)
    try:
        categories_manager.category_update(category_to_update)
        return jsonify({
            "status": "success",
            "message": "Category updated successfully!"
        }), 200
    except SQLAlchemyError:
        return jsonify({
            "message": "An error occurred while deleting category. Something wrong with the database"
        }), 500
    except NoResultFound:
        return jsonify({
            "message": "No such category exists. Why are you change the id ?))))"
        }), 400


# Dashboard Tables
@api_dashboard_bp.route('/contracts_ending', methods=['GET'])
@login_required
def contracts_ending():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    dashboard_instance = DashBoard(db.session)
    response = dashboard_instance.get_card_inf_apiget_contracts_information_date_api(per_page, offset)
    return jsonify(response)


@api_dashboard_bp.route('/contracts_ending_amount', methods=['GET'])
@login_required
def contracts_ending_amount():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    dashboard_instance = DashBoard(db.session)
    response = dashboard_instance.get_contracts_information_amount_api(per_page, offset)
    return jsonify(response)


# Api for users table

@api_users_bp.route('/all_users', methods=['GET'])
@login_required
def all_users_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'User Name')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_users.get(order_by, ("id", User))
    search_engine = UserSearchEngine(db.session)
    user_list, total_count = search_engine.get_all_results_api(per_page, offset, direction, mapping_results)
    response = {
        "data": user_list,
        "total_count": total_count
    }
    return jsonify(response)


@api_users_bp.route('/all_users/<string:search>', methods=['GET'])
@login_required
def get_search(search):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page
    order_by = request.args.get('order_by', 'User Name')
    direction = request.args.get('dir', 'desc')
    mapping_results = column_map_users.get(order_by, ("id", User))
    search_engine = UserSearchEngine(db.session, search)
    user_list, total_count = search_engine.search_query_api(per_page, offset, direction, mapping_results)
    response = {
        "data": user_list,
        "total_count": total_count
    }
    return jsonify(response)