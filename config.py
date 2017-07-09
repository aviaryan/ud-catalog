class Auth:
    """
    Auth class contains details for flow used in OAuth authentication
    using Google
    """
    # OAuth credentials
    CLIENT_ID = '<insert client id here>'
    CLIENT_SECRET = '<insert client secret here>'
    # URI that google server will redirect to
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    # Endpoint to start OAuth request from
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    # Endpoint to fetch user token
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    # Endpoint to get user information at the end of oauth
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    # Data we plan to access from Google profile
    SCOPE = ['profile', 'email']
