from requests_oauthlib import OAuth2Session
from flask_login import current_user
from config import Auth
from catalog.models import Category, Item


def get_google_auth(state=None, token=None):
    """
    get_google_auth creates an oauth object for google oauth
    Thanks http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
    """
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


def categories_to_json(categories):
    """
    categories_to_json converts categories SQLAlchemy object to json object
    """
    main = {}
    main['categories'] = []
    for cat in categories:
        catDict = {}
        catDict['id'] = cat.id
        catDict['name'] = cat.name
        catDict['items'] = []
        for item in cat.items:
            itemDict = {}
            itemDict['id'] = item.id
            itemDict['title'] = item.title
            itemDict['description'] = item.description
            catDict['items'].append(itemDict)
        main['categories'].append(catDict)
    return main


def get_category_list():
    """
    get_category_list returns list of all categories
    """
    return [c.name for c in Category.query.all()]


def is_not_authorized(item_id):
    """
    is_not_authorized checks if user is not authorized to access a page
    This means he is not the one who created that item
    """
    item = Item.query.get(int(item_id))
    return item.user.id != current_user.id
