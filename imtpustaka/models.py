from datetime import datetime
from datetime import timedelta
import pytz
from imtpustaka import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nim = db.Column(db.Integer, unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.nim}')"


class Book(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(12), nullable=False)
    availability = db.Column(db.Boolean(), nullable=False, default=True)
    count = db.Column(db.Integer, nullable=False, default=0)
    def __repr__(self):
        return f"Book('{self.id}', '{self.title}', '{self.category}', {self.availability}')"

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    title_id = db.Column(db.Integer, nullable=False)
    name_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.now()+timedelta(hours=7))
    date_end = db.Column(db.DateTime)

    def __repr__(self):
        return f"Log('{self.title}', '{self.name}', {self.date_start}', '{self.date_end}')"
