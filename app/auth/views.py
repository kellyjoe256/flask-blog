from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, abort)
from flask_login import login_user, login_required, logout_user
from app.auth.forms import LoginForm, RegistrationForm
from app import db
from app.models import User
from app.utils import is_email, guest_required, is_safe_url

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
@guest_required('/admin')
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username_email = form.username_email.data
        password = form.password.data

        if is_email(username_email):
            user = User.query.filter_by(email=username_email).first()
        else:
            user = User.query.filter_by(username=username_email).first()

        if user is not None and user.verify_password(
                password) and user.active:
            # log user in
            login_user(user)

            next_url = request.args.get('next')

            # is_safe_url should check if the url is safe for redirects
            if not is_safe_url(next_url):
                return abort(400)

            return redirect(next_url or url_for('admin.dashboard'))
        else:
            # when login details are incorrect
            flash('Please check your credentials', 'danger')
    data = {
        'title': 'Login',
        'form': form,
    }
    return render_template('auth/login.html', **data)


@auth.route('/register', methods=['GET', 'POST'])
@guest_required('/admin')
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        user.name = form.name.data
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()

        flash('You have successfully registered! You may now login', 'success')
        # redirect to the login page
        return redirect(url_for('auth.login'))

    data = {
        'title': 'Register',
        'form': form,
    }
    return render_template('auth/register.html', **data)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully been logged out', 'success')
    # redirect to the login page
    return redirect(url_for('auth.login'))
