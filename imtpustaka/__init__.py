from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = '592abcbfb5b3b7c14a76b78ac56fbcfe308ee6632fc4d8d406cb57397b92d109'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bohrqglvlkqsfw:592abcbfb5b3b7c14a76b78ac56fbcfe308ee6632fc4d8d406cb57397b92d109@ec2-54-225-242-183.compute-1.amazonaws.com:5432/d9a1i833q87s2m'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from imtpustaka import routes
