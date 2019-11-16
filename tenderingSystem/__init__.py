from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0e0a39dfc12b0c9d0497ee00aa3c9b466b5638899e9e44b37f2cd3698176819c1c6df0c74a0fa6489623b2b4b1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tendering_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tendering_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "your session has timed out. login to access this page"
login_manager.login_message_category = "warning"
from tenderingSystem import routes
