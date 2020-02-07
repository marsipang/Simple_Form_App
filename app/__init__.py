import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#from models import User

from Login import login_bp
from Application import application_bp
from Tables import tables_bp

app.register_blueprint(login_bp)
app.register_blueprint(application_bp)
app.register_blueprint(tables_bp, url_prefix='/tables')