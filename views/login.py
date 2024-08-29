from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from extensions import login_manager
from database.db_init import db
from database.models import User
from forms.login import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint('login', __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        password = form.password.data
        if user and password == user.password:
            login_user(user, remember=user.id)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.home'))
    return render_template("auth.html", form=form)


@login_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login.login'))