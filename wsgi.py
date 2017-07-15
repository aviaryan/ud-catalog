from catalog import app as app
import sys

sys.path.insert(0, '/var/www/catalog')
app.secret_key = 'New secret key. Change it on server'
