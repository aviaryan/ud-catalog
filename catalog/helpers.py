from requests_oauthlib import OAuth2Session
from config import Auth


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
