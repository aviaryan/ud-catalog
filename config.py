class Auth:
    CLIENT_ID = ('153367843910-6trc0vmgk73pqsu61fou4a4npbckf94u'
                 '.apps.googleusercontent.com')
    CLIENT_SECRET = 'cTmDcWFQk_kFaLV5q17Wleb3'
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']
