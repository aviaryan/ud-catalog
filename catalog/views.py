import json
from datetime import datetime

from catalog import app, db
from flask_login import current_user, login_user, login_required, logout_user
from flask import render_template, redirect, url_for, session, request,\
    jsonify
from requests.exceptions import HTTPError

from config import Auth
from catalog.helpers import get_google_auth, categories_to_json
from catalog.models import User, Category, Item


@app.route('/')
def index():
    categories = [c.name for c in Category.query.all()]
    return render_template('home.html', categories=categories)


@app.errorhandler(404)
def page_not_found(error):
    return '404. This page does not exist', 404


@app.route('/catalog.json')
def get_catalog():
    catalog = Category.query.all()
    return jsonify(categories_to_json(catalog))


@app.route('/new')
def new_item():
    return render_template(
        'item_form.html', item=Item(), categories=Category.query.all(),
        target_url=url_for('new_item_save'))


@login_required
@app.route('/new', methods=['POST'])
def new_item_save():
    form = request.form
    item = Item()
    item.category_id = int(form['category'])
    item.title = form['title']
    item.description = form['description']
    item.created_at = datetime.now()
    item.user_id = current_user.id
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('index'))


# ##########
# AUTH VIEWS
# ##########


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return redirect(auth_url)


@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(token)
            user.token = json.dumps(token)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
