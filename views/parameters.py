from flask import Blueprint, render_template, redirect, flash, url_for, current_app, abort
from sqlalchemy.exc import OperationalError, NoResultFound
from forms.categories_form import SearchForm
from database.db_init import db
from database.validators import CategoriesSearchEngine, EditCategory
from forms.custom_validators import add_contract_pdf
from forms.edit_category import EditCategoryForm
from forms.filters import *

parameter_bp = Blueprint('parameters', __name__)


@parameter_bp.route('/categories', methods=['GET'])
def categories():
    form = SearchForm()
    update_form = EditCategoryForm()
    return render_template('categories.html', form=form, update_form=update_form)


@parameter_bp.route('/categories/edit_category/<int:category_id>', methods=['GET'])
def edit_category(category_id):
    try:
        form = EditCategoryForm()
        search_engine = CategoriesSearchEngine(db.session, category_id)
        search_result = search_engine.search_category()
        return render_template('edit_category.html',
                               form=form,
                               search_result=search_result,
                               id=category_id)
    except NoResultFound:
        abort(404)


@parameter_bp.route('/categories/update_category/<int:category_id>', methods=['POST'])
def update_category(category_id):
    form = EditCategoryForm()
    if form.validate_on_submit():
        try:
            new_name = sanitize_company(form.category.data)
            search_engine = EditCategory(db.session, category_id)
            search_result = search_engine.category_update(new_name)
            if search_result:
                flash("The category was updated successfully", "success")
                return redirect(url_for('parameters.edit_category', category_id=category_id))
            flash("The error occurred on the database", "error")
            return render_template('edit_category.html',
                                   form=form,
                                   search_result=search_result,
                                   id=category_id)
        except NoResultFound:
            abort(404)