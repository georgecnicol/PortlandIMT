# core/views.py
# https://console.developers.google.com/
# TODO change the the URL in the OAuth authorized URI from localhost to deployment URL
# TODO currently it says: http://127.0.0.1:5000/login/google/authorized

from flask import render_template, redirect, Blueprint, url_for, flash
from flask_login import login_user, logout_user, login_required
from project.users.forms import RegisterForm, LoginForm
from flask_dance.contrib.google import make_google_blueprint, google
from project.models import User
from project import db


# TODO make env variables on production?
core = Blueprint('core', __name__, template_folder = 'templates/core')
with open('/Users/admin/website/secret.txt') as fh:
    details = fh.read().split()
    client_id = details[1]
    client_secret = details[2]


# registered in project.__init__
g_blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    # reprompt_consent=True,
    offline=True,
    scope=["profile", "email"]
)


@core.route('/')
def index():
    return render_template('index.html')


@core.route('/about')
def about():
    return render_template('about.html')


@core.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data.lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            # flash(f'Welcome {user.first}') # needs jumbotron on index to display properly
            return redirect(url_for('core.index'))
        else:
            flash(f'There is no combination of {form.email.data} with that password')
    else:
        pass
    return render_template('login.html', form = form)


# TODO - some kind of captcha and key for registering
# TODO - implement https://pypi.org/project/captcha/
@core.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.check_email_unique(form.email.data):
            phone = form.area.data + form.exchange.data + form.subscriber.data
            new_user = User(form.email.data.lower(), form.first.data.capitalize(),
                            form.last.data.capitalize(), form.password.data,
                            phone, form.email_me.data, form.text_me.data)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Welcome {new_user.first}, you are now registered. Please login to continue.')
            return redirect(url_for('users.login'))
        else:
            flash(f'Sorry, the email {form.email.data} has already been registered. '
                  f'Perhaps try to login with the \'I forgot my password\' option')
            form.email.data = ''
            form.password.data = ''
            form.pass_confirm.data = ''

    return render_template('register.html', form = form)


@core.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))




