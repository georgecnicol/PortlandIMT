# core/views.py
# https://console.developers.google.com/
# https://pusher.com/tutorials/google-recaptcha-flask
import os
from flask import render_template, redirect, Blueprint, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from project.users.forms import RegisterForm, LoginForm
from flask_dance.contrib.google import make_google_blueprint, google
from project.models import User
from project import db, get_config

# routes here:
#
# @core.route('/google') .. oauth_login
# @core.route('/') .. index
# @core.route('/about')
# @core.route('/login', methods = ['GET', 'POST'])
# @core.route('/register', methods = ['GET', 'POST'])
# @core.route('/logout')


os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
core = Blueprint('core', __name__, template_folder = 'templates/core')
config = get_config() # used in g_blueprint and register view

# registered in project.__init__
g_blueprint = make_google_blueprint(
    client_id=config.get('client_id'),
    client_secret=config.get('client_secret'),
    # reprompt_consent=True,
    #coffline=True,
    scope=["https://www.googleapis.com/auth/userinfo.email"]
)

# a website user who attempts to login using google
# and has a valid google auth, will leave a token of that auth
# we need to delete that token when they logout or if they aren't actually registered
def de_auth_google():
    try:
        token = g_blueprint.token["access_token"]
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params = {"token": token},
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        )
        if resp.ok:
            del g_blueprint.token
    except TypeError:
        pass # no token for manual login people

# trying to match their google auth gmail to a registered user's email
# if we can, we log them in. Otherwise we need to get rid of their token
# which is the edge case, where they try to sign in using google, but haven't registered
# for the try/except, we don't actually care if they didn't have a token, we were just
# checking if they did and then cleaning it up if they did.
def match_gmail():
    try:
        resp = google.get("/oauth2/v2/userinfo")
        gmail = resp.json()["email"]
        user = User.query.filter_by(email = gmail).first()
        if user is not None:
            login_user(user)
        else:
            de_auth_google()
    except KeyError:
        pass

# log in with google
# this page wants to end up because of flask dance as:
# https://xxxxxx.com/login/google
# since there is already a blueprint directing it to /login
# the route.('/login/google') take it to /login/login/google
@core.route('/google')
def oauth_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    # otherwise:
    # see if we get a valid response from google about their gmail
    # and if that gmail exists in our db, they get logged in
    # otherwise they just go back to index as an outside viewer
    return redirect(url_for('core.index'))


@core.route('/')
@core.route('/index')
def index():
    match_gmail()
    return render_template('index.html')


@core.route('/about')
def about():
    return render_template('about.html')


# login using the email/ password method
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


@core.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.token.data == config.get('reg_token').strip():
            if form.check_email_unique(form.email.data):
                phone = form.area.data + form.exchange.data + form.subscriber.data
                new_user = User(form.email.data.lower(), form.first.data.capitalize(),
                                form.last.data.capitalize(), form.password.data,
                                phone, form.email_me.data, form.text_me.data)
                db.session.add(new_user)
                db.session.commit()
                flash(f'Welcome {new_user.first}, you are now registered. Please login to continue.')
                return redirect(url_for('core.login'))
            else:
                flash(f'Sorry, the email {form.email.data} has already been registered. '
                      f'Perhaps try to login with the \'I forgot my password\' option')
                form.email.data = ''
                form.password.data = ''
                form.pass_confirm.data = ''
        else: # bad token
            flash(f'The registration token provided is not correct.')
            form.token.data = ''

    return render_template('register.html', form = form)


@core.route('/logout')
@login_required
def logout():
    de_auth_google()
    logout_user()

    return redirect(url_for('core.index'))




