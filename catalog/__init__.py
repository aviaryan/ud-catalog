import os

from flask import Flask, g, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

# allow http transport
# (https requires ssl keys, not good for local testing)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# init flask app
app = Flask(__name__)

# base config
# app.config.from_object('config.Config')

# default values
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
    + os.path.join(basedir, '../database.sqlite3')

app.config['CSRF_ENABLED'] = True
app.secret_key = 'no one can guess this'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.debug = True

# login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

# database
db = SQLAlchemy(app)

# down for circular imports
import catalog.views
import catalog.models
from catalog.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('unauthorized.html', not_logged_in=True)


@app.before_request
def set_login_status():
    if current_user.is_authenticated:
        g.auth_uri = url_for('logout')
        g.button_text = 'Logout'
        g.logged_in = True
        return
    g.auth_uri = url_for('login')
    g.button_text = 'Login'
    g.logged_in = False
