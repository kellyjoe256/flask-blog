from flask import (Blueprint, render_template, request, redirect, url_for, flash)
from flask_login import login_required, current_user
from app import db
from app.admin.forms import ChangePasswordForm

admin = Blueprint('admin', __name__)


@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    data = {
        'title': 'Dashboard',
    }
    return render_template('admin/index.html', **data)


@admin.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()

        flash('Password changed successfully', 'success')

        return redirect(url_for('admin.dashboard'))

    data = {
        'title': 'Change Password',
        'form': form,
    }
    return render_template('admin/change_password.html', **data)
