from datetime import datetime
from catalog import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    User model to store app users
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(100))
    token = db.Column(db.Text)
    items = db.relationship('Item', backref="user", uselist=True)


class Category(db.Model):
    """
    Category model to store different categories
    """
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('Item', backref="category", uselist=True)


class Item(db.Model):
    """
    Item model stores individual items and links them
    to category and user
    """
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.now())

    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
