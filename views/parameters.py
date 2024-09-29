from flask import Blueprint, render_template, redirect, flash, url_for, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound, OperationalError, DBAPIError
from werkzeug.security import generate_password_hash
from database.models import User
from forms.add_user import CreateUserForm
from forms.categories_form import SearchForm
from database.db_init import db
from database.validators import CategoriesSearchEngine, EditCategory, UserManager, UserSearchEngine, EditUser
from forms.edit_category import EditCategoryForm
from forms.edit_user_form import EditUserForm
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
                               categoty_id=category_id)
    except NoResultFound:
        abort(404)


@parameter_bp.route('/categories/update_category/<string:category_id>', methods=['POST'])
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
                flash("Kateqoriya uğurla yeniləndi", "success")
                return redirect(url_for('parameters.edit_category', category_id=category_id))
            flash("Səhv verilənlər bazasında baş verdi", "error")
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
        user_name = filter_username(form.username.data)
        role = form.role.data
        user_manager = UserManager(db.session)
        user_exist = user_manager.is_user_existed(user_name)
        if user_exist:
            flash("İstifadəçi artıq mövcuddur", "warning")
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
                flash("İstifadəçi uğurla yaradıldı", "success")
                return redirect(url_for('parameters.create_user'))
            except OperationalError:
                flash("Verilənlər bazası tərəfində xəta baş verdi. Zəhmət olmasa sonra yenidən əlavə edin", "error")
                db.session.rollback()
                return render_template('create_user.html', form=form)


@parameter_bp.route('/edit_user/<int:user_id>', methods=['GET'])
@login_required
def edit_user(user_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    try:
        search_engine = UserSearchEngine(db.session, user_id)
        search_result = search_engine.search_user()
        form = EditUserForm(role=search_result.role)
        return render_template("edit_user.html",
                               search_result=search_result,
                               form=form,
                               user_id=user_id
                               )
    except NoResultFound:
        abort(404)


@parameter_bp.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    search_engine = UserSearchEngine(db.session, user_id)
    user_manager = UserManager(db.session)
    edit_engine = EditUser(db.session, user_id)
    original_data = search_engine.search_user()
    form = EditUserForm(role=original_data.role)
    all_roles = form.role.choices
    values = [role for role, _ in all_roles]
    if form.role.data not in values:
        flash('Yanlış kateqoriya seçilib. Zəhmət olmasa düzgün seçimi edin', 'error')
        return redirect(url_for('parameters.edit_user', user_id=user_id))
    if form.validate_on_submit():
        user_exist = user_manager.is_user_existed(form.username.data)
        if user_exist:
            flash("İstifadəçi artıq mövcuddur", "warning")
            return render_template('edit_user.html', form=form, user_id=user_id,
                                   search_result=original_data)
        hashed_password = generate_password_hash(form.password.data, salt_length=10)
        try:
            data_dict = dict(
                username=form.username.data if form.username.data else None,
                password=hashed_password if form.password.data else None,
                role=form.role.data if form.role.data else None
            )
            success, message = edit_engine.update_data(data_dict)
            if success:
                db.session.commit()
                flash(message, "success")
                return redirect(url_for('parameters.all_users', user_id=user_id))
            else:
                db.session.rollback()
                flash(message, "warning")
                return render_template('edit_user.html', form=form, user_id=user_id,
                                       search_result=original_data)
        except NoResultFound:
            db.session.rollback()
            flash("İstifadəçi verilənlər bazasında tapılmadı", "error")
            return render_template('edit_user.html', form=form, user_id=user_id,

                                   search_result=original_data)
        except DBAPIError:
            db.session.rollback()
            flash("Error in database", "error")
            return render_template('edit_user.html', form=form, user_id=user_id, search_result=original_data)
    flash("İstifadəçi verilənlər bazasında tapılmadı", "warning")
    return render_template('edit_user.html', form=form, user_id=user_id, search_result=original_data)


@parameter_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    user_manager = UserManager(db.session)
    try:
        user_manager.delete_user(user_id)
        flash("İstifadəçi uğurla silindi", "success")
        db.session.commit()
        return jsonify({
            'status': 'success',
        }), 200
    except NoResultFound:
        abort(404)
    except OperationalError:
        flash("Xəta baş verdi. Əməliyyat bərpa edildi", "error")
        db.session.rollback()
        return jsonify({
            'status': 'error',
        }), 500


@parameter_bp.route('/all_users', methods=['GET'])
@login_required
def all_users():
    form = CreateUserForm()
    if current_user.role == "viewer" or current_user.role == "editor":
        abort(401)
    return render_template('check_users.html', form=form)
