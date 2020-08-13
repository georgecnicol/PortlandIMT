# project/__init__.py
import os
import json
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager

def get_config():
    with open('/etc/PIMT/config.json') as config_file:
        config = json.load(config_file)
    return config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# send them here if they try to access a page that requires login
login_manager.login_view = 'core.login'


def create_app():
    app = Flask(__name__)
    config = get_config()

    # recaptcha
    app.config['RECAPTCHA_PUBLIC_KEY'] = config.get('captcha_public')
    app.config['RECAPTCHA_PRIVATE_KEY'] = config.get('captcha_private')
    app.config['RECAPTCHA_USE_SSL'] = False

    # csrf
    app.config['SECRET_KEY'] = config.get('csrf')


    # database setup
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
    app.config['RENDER_AS_BATCH'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # register blueprints #############
    from project.errors.handlers import errors
    from project.core.views import core, g_blueprint
    from project.users.views import users
    from project.appointments.views import appointments
    app.register_blueprint(appointments, url_prefix = '/appointments')
    app.register_blueprint(core)            # no prefix because this is views off the core
    app.register_blueprint(g_blueprint, url_prefix = '/login')
    app.register_blueprint(errors, url_prefix = '/errors')
    app.register_blueprint(users, url_prefix = '/users')

    # OATH SETUP #############
    # for local only
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'

    return app
