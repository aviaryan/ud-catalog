from catalog import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    User class
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(100))
    token = db.Column(db.Text)
