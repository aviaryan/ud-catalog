import sys

sys.path.insert(0, '/var/www/catalog')

from catalog import app as app

app.secret_key = 'New secret key. Change it on server'
