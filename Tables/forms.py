#Define packages
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email

class AddUser(Form):
    firstname = TextField('First Name', validators=[DataRequired()])
    lastname = TextField('Last Name', validators=[DataRequired()])
    email = TextField('Email Address', validators=[DataRequired(), Email()])


