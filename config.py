class Auth:
    """
    Auth class contains details for flow used in OAuth authentication
    using Google
    """
    CLIENT_ID = '<insert client id here>'
    CLIENT_SECRET = '<insert client secret here>'
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']
