# login with gmail
# logout - partially done ... check when google logout if additional

from flask import render_template, redirect, url_for, Blueprint, flash, abort
from flask_login import current_user, logout_user, login_required
from project import db, login_manager
from project.models import User
from project.users.forms import UpdateEmailForm
from project.users.forms import AlterAdminForm, UpdatePasswordForm, UpdatePhoneForm

users = Blueprint('users', __name__, template_folder = 'templates/users') # register this in init

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@users.route('/update-email', methods = ['GET', 'POST'])
@login_required
def update_email():
    form = UpdateEmailForm()
    old_email = current_user.email
    if form.validate_on_submit():
        if form.check_email_unique(form.email.data):
            current_user.email = form.email.data
            current_user.email_me = form.email_me.data
            db.session.commit()
            logout_user()
            flash(f'Please log back in with your updated email address {form.email.data}')
            return redirect(url_for('core.login'))
        else:
            flash(f'{form.email.data} is already in use.')
    else:
        if form.email.data:
            flash(f'{form.email.data} does not appear to be a valid email address.')

    form.email.data = ''
    return render_template('update-email.html', form = form, old_email = old_email)


@users.route('/update-password', methods = ['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_new_password(form.new_password.data)
            db.session.commit()
            logout_user()
            flash(f'Please login with your new password.')
            return redirect(url_for('core.login'))
        else:
            form.old_password.data = ''
            form.new_password.data = ''
            form.confirm_pass.data = ''
            flash(f'Old password does not match, please try again.')
    return render_template('update-password.html', form = form)


@users.route('/update-phone', methods = ['GET', 'POST'])
@login_required
def update_phone():
    form = UpdatePhoneForm()
    if form.validate_on_submit():
        current_user.phone = form.area.data + form.exchange.data + form.subscriber.data
        current_user.text_me = form.text_me.data
        db.session.commit()
        flash(f'Your phone information has been changed.')
        return redirect(url_for('users.account'))
    return render_template('update-phone.html', form = form)


# admin only screen
@users.route('/show', methods = ['GET', 'POST'])
@login_required
def show():
    if current_user.is_admin:
        users = User.query.filter_by(is_admin = 0).order_by(User.last).all()
        admins = User.query.filter_by(is_admin = 1).order_by(User.last).all()
        form = AlterAdminForm()
        # add/remove admin
        if form.validate_on_submit():
            user = User.query.filter_by(email = form.email.data.lower()).first()
            if user is not None:
                user.set_admin(form.add_or_remove.data)
                db.session.commit()

        return render_template('show-users.html', form = form, admins = admins, users = users)
    else:
        abort(403)


@users.route('/account')
@login_required
def account():
    return render_template('account.html', user = current_user)
