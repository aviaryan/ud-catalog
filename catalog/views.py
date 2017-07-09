import json
from datetime import datetime

from catalog import app, db
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import desc
from flask import render_template, redirect, url_for, session, request,\
    jsonify
from requests.exceptions import HTTPError

from config import Auth
from catalog.helpers import get_google_auth, categories_to_json, \
    get_category_list
from catalog.models import User, Category, Item


@app.route('/')
def index():
    items = Item.query.order_by(desc(Item.id)).limit(10).all()
    return render_template(
        'home.html', categories=get_category_list(), items=items)


@app.errorhandler(404)
def page_not_found(error):
    return '404. This page does not exist', 404


@app.route('/catalog.json')
def get_catalog():
    catalog = Category.query.all()
    return jsonify(categories_to_json(catalog))


@app.route('/new')
@login_required
def new_item():
    return render_template(
        'item_form.html', item=Item(), categories=Category.query.all(),
        target_url=url_for('new_item_save'))


@app.route('/new', methods=['POST'])
@login_required
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


@app.route('/catalog/<category>')
def list_category(category):
    category = category.replace('-', ' ')
    # thanks https://stackoverflow.com/questions/4985762/
    items = Item.query.join(Category).filter(Category.name == category)\
        .order_by(desc(Item.id)).all()
    return render_template(
        'category.html', category=category, items=items,
        categories=get_category_list()
    )


@app.route('/catalog/<category>/<item>')
def item_view(category, item):
    title = item.replace('-', ' ')
    item = Item.query.filter(Item.title == title).first()
    return render_template('item_show.html', item=item, user=item.user)


@app.route('/catalog/<category>/<item_id>/edit')
@login_required
def edit_item(category, item_id):
    item = Item.query.get(int(item_id))
    return render_template(
        'item_form.html', item=item, categories=Category.query.all(),
        target_url=url_for('save_item', item_id=item.id))


@app.route('/catalog/<item_id>/save', methods=['POST'])
@login_required
def save_item(item_id):
    form = request.form
    item = Item.query.get(int(item_id))
    item.category_id = int(form['category'])
    item.title = form['title']
    item.description = form['description']
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/catalog/<category>/<item_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(category, item_id):
    if request.method == 'GET':
        item = Item.query.get(int(item_id))
        return render_template(
            'item_delete.html', item=item, target_url=url_for(
                'delete_item', category=category, item_id=item.id
            ))
    else:
        Item.query.filter(Item.id == int(item_id)).delete()
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
