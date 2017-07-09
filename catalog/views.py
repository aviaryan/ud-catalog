from catalog import app
from flask import render_template


@app.route('/')
def index():
    return render_template('home.html')


@app.errorhandler(404)
def page_not_found(error):
    return '404. This page does not exist', 404
