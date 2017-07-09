# Udacity Catalog

Udacity FSND project


## Running instructions

Tested on **Python 3**.

* Install requirements.

```sh
pip install -r requirements.txt
```

* Setup database.

```sh
# python manage.py db init     # init migrations folder at project start
# python manage.py db migrate  # generate migration files in case of model change
python manage.py db upgrade  # upgrade database
```

* Create initial categories.

```sh
python create_category.py
```

* Start server.

```sh
python manage.py runserver
```


## Generating Google OAuth token

* Create an app on developers.google.com.
* Click on Credentials -> OAuth token.
* Make sure you have `http://localhost:5000` in authorized JavaScript origins and `http://localhost:5000/gCallback` in Redirect URIs.
* Get your client ID and client secret.
* Put it in `config.py`.
