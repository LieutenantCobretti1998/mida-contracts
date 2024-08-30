from flask import Blueprint, render_template, redirect, flash, url_for, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound, OperationalError
from werkzeug.security import generate_password_hash
from database.models import User
from forms.add_user import CreateUserForm
from forms.categories_form import SearchForm
from database.db_init import db
from database.validators import CategoriesSearchEngine, EditCategory, UserManager
from forms.edit_category import EditCategoryForm
from forms.filters import *

parameter_bp = Blueprint('parameters', __name__)


@parameter_bp.route('/categories', methods=['GET'])
@login_required
def categories():
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    form = SearchForm()
    update_form = EditCategoryForm()
    return render_template('categories.html', form=form, update_form=update_form)


@parameter_bp.route('/categories/edit_category/<int:category_id>', methods=['GET'])
@login_required
def edit_category(category_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
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
@login_required
def update_category(category_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
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


@parameter_bp.route('/users', methods=['GET'])
@login_required
def create_user():
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    form = CreateUserForm()
    return render_template('create_user.html', form=form)


@parameter_bp.route('/save_user', methods=['POST'])
@login_required
def save_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        password = generate_password_hash(form.password.data, salt_length=10)
        user_name = form.username.data
        role = form.role.data
        user_manager = UserManager(db.session)
        user_exist = user_manager.is_user_existed(user_name)
        if user_exist:
            flash("User already exists", "warning")
            return render_template('create_user.html', form=form)
        else:
            try:
                user = User(
                    username=user_name,
                    password=password,
                    role=role,
                )
                db.session.add(user)
                db.session.commit()
                flash("User created successfully", "success")
                return redirect(url_for('parameters.create_user'))
            except OperationalError:
                flash("Something went wrong on database side. Please add again later", "error")
                db.session.rollback()
                return render_template('create_user.html', form=form)


@parameter_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    print(user_id)
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    user_manager = UserManager(db.session)
    try:
        user_manager.delete_user(user_id)
        flash("User deleted successfully", "success")
        db.session.commit()
        return jsonify({
            'status': 'success',
        }), 200
    except NoResultFound:
        abort(404)
    except OperationalError:
        flash("Something went wrong. transaction was restored", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500


@parameter_bp.route('/all_users', methods=['GET'])
@login_required
def all_users():
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    return render_template('check_users.html')
