#Define packages
from flask_wtf import Form
from wtforms import PasswordField, TextField
from wtforms.validators import DataRequired, Length, EqualTo, Email

#Login and Signup Forms
class LoginForm(Form):
    username = TextField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:')
    #remember_me = BooleanField('Remember Me') 
    #submit = SubmitField('Sign In')

class ForgotPassword(Form):
    username = TextField('Email:', validators=[DataRequired(), Email()])
    confirmcode = PasswordField('Confirmation Code:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=6, max=25)])
    confirm = PasswordField('Confirm password:', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])