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
    get_category_list, is_not_authorized
from catalog.models import User, Category, Item


@app.route('/')
def index():
    """
    index loads the home page of the project
    """
    items = Item.query.order_by(desc(Item.id)).limit(10).all()
    return render_template(
        'home.html', categories=get_category_list(), items=items)


@app.errorhandler(404)
def page_not_found(error):
    return '404. This page does not exist', 404


@app.route('/catalog.json')
def get_catalog():
    """
    returns the full catalog of items in json format
    """
    catalog = Category.query.all()
    return jsonify(categories_to_json(catalog))


@app.route('/new')
@login_required
def new_item():
    """
    displays form to create a new item
    """
    return render_template(
        'item_form.html', item=Item(), categories=Category.query.all(),
        target_url=url_for('new_item_save'))


@app.route('/new', methods=['POST'])
@login_required
def new_item_save():
    """
    saves the new item to db
    """
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
    """
    lists items in a specific category
    """
    # spaces were replaced by dashes to make urls look better
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
    """
    shows a specific item
    The <catalog> in url has been added for eye candy
    """
    title = item.replace('-', ' ')
    item = Item.query.filter(Item.title == title).first()
    return render_template('item_show.html', item=item, user=item.user)


@app.route('/catalog/<category>/<item_id>/edit')
@login_required
def edit_item(category, item_id):
    """
    shows edit page for a specific item
    """
    # authorization check
    if is_not_authorized(item_id):
        return render_template('unauthorized.html')
    item = Item.query.get(int(item_id))
    return render_template(
        'item_form.html', item=item, categories=Category.query.all(),
        target_url=url_for('save_item', item_id=item.id))


@app.route('/catalog/<item_id>/save', methods=['POST'])
@login_required
def save_item(item_id):
    """
    saves an item after edit
    """
    # authorization check
    if is_not_authorized(item_id):
        return render_template('unauthorized.html')
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
    """
    shows delete page for an item
    Also implements the backend logic to actually delete it
    """
    # authorization check
    if is_not_authorized(item_id):
        return render_template('unauthorized.html')
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
    """
    login handler route
    redirects to Google oauth uri if user is not logged in
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    # get google oauth url
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    # set oauth state
    session['oauth_state'] = state
    # redirect to google for auth
    return redirect(auth_url)


@app.route('/gCallback')
def callback():
    """
    google callback route
    """
    # redirect to home page if user is logged in
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    # check for errors
    if 'error' in request.args:
        # user denied access to their account
        if request.args.get('error') == 'access_denied':
            return 'Access denied by user'
        # some unknown error occured
        return 'Some error has occured. Please try again'
    # missing state information in the callback
    # something went wrong, login again
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    # successful authentication confirmed at this point
    google = get_google_auth(state=session['oauth_state'])
    try:
        # fetch token from google servers
        token = google.fetch_token(
            Auth.TOKEN_URI,
            client_secret=Auth.CLIENT_SECRET,
            authorization_response=request.url)
    except HTTPError as e:
        return 'HTTPError occurred: ' + str(e)
    # get handler for server token
    google = get_google_auth(token=token)
    # get user info now that we have token for user
    resp = google.get(Auth.USER_INFO)
    if resp.status_code == 200:
        # user data fetched
        user_data = resp.json()
        email = user_data['email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            # create new user if user with the email didn't exist
            user = User()
            user.email = email
        user.name = user_data['name']
        user.token = json.dumps(token)
        # save user to database
        db.session.add(user)
        db.session.commit()
        # login user now using flask_login
        login_user(user)
        return redirect(url_for('index'))
    return 'Error when fetching user information from Google'


@app.route('/logout')
@login_required
def logout():
    """
    log user out of the system
    uses flask_login method
    """
    logout_user()
    return redirect(url_for('index'))
