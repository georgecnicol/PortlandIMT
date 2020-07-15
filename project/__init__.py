# project/__init__.py
import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
with open('/Users/admin/website/secret.txt', 'r') as fh:
    app.config['SECRET_KEY'] = fh.read().split()[0]

###### DATABASE SETUP ############
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['RENDER_AS_BATCH'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.create_all()


# OATH SETUP #############
# for local only #########
# TODO - can be removed in production
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'

# login configs #############
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

# register blueprints #############
from project.errors.handlers import errors
from project.core.views import core, g_blueprint
from project.users.views import users
from project.appointments.views import appointments
app.register_blueprint(appointments, url_prefix = '/appointments')
app.register_blueprint(core)            # no prefix because this is views off the core
app.register_blueprint(g_blueprint)     # no prefix because this is also views off the core
app.register_blueprint(errors, url_prefix = '/errors')
app.register_blueprint(users, url_prefix = '/users')

