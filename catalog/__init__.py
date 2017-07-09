import os

from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

# allow http transport
# (https requires ssl keys, not good for local testing)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# init flask app
app = Flask(__name__)

# default values
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set database uri for SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
    + os.path.join(basedir, '../database.sqlite3')

app.config['CSRF_ENABLED'] = True
app.secret_key = 'no one can guess this'
# enable debug for auto reloads
app.debug = True

# login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

# database
db = SQLAlchemy(app)

# these imports listed below to resolve circular imports
import catalog.views
import catalog.models
from catalog.models import User


@login_manager.user_loader
def load_user(user_id):
    """
    user loader for flask_login
    This method helps flask_login to fetch current user
    """
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    """
    This function implements what happens when an authenticated
    route is called and user is not authenticated
    """
    return render_template('unauthorized.html', not_logged_in=True)


@app.before_request
def set_login_status():
    """
    set current login status
    Used in jinja templates
    """
    if current_user.is_authenticated:
        g.logged_in = True
        g.user_email = current_user.email
    else:
        g.logged_in = False
