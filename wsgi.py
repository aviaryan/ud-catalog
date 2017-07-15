import sys

sys.path.insert(0, '/var/www/catalog')


from catalog import app as application

application.secret_key = 'New secret key. Change it on server'

application.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://'
    'catalog:password@localhost/catalog')
