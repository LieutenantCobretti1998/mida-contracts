from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from extensions import login_manager
from database.db_init import db
from database.models import User
from forms.login import LoginForm

login_bp = Blueprint('login', __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user:
            print(user.username)
            login_user(user, remember=user.id)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.home'))
    return render_template("auth.html", form=form)

