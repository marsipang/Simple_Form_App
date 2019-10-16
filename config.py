import os, sys, pythoncom
from functools import wraps
from flask import redirect, url_for, session
from win32com.client import Dispatch
#basedir = os.path.abspath(os.path.dirname(__file__))

gitfolder = os.path.dirname(os.path.realpath(sys.argv[0])).replace('\\', '/') + '/'
host = '''host website path'''

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'example-secret-key-demo'
    database = "website.db"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(gitfolder, 'website.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


#Create login wrap
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login.login'))
    return wrap

def logged_in_reroute(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('application.home'))
        else:
            return f(*args, **kwargs)
    return wrap

def send_email(to, subj, body):
    pythoncom.CoInitialize()
    outlook = Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subj
    mail.Body = body
    mail.Send()
