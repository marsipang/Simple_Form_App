from flask import render_template, redirect, url_for, request, session, Blueprint
from Login.forms import LoginForm, ForgotPassword
from werkzeug.security import generate_password_hash, check_password_hash
from config import send_email, logged_in_reroute, login_required
from sql import sql_pull, sql_edit
import string, random

login_bp = Blueprint('login', __name__, template_folder='templates')

#Create Welcome, Login, and Sign up pages
@login_bp.route('/', methods=['GET', 'POST'])
@logged_in_reroute
def welcome():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = sql_pull('''SELECT * FROM USERS WHERE EMAIL = "%s"''' % request.form['username'])
            if 'Forgot Password' in request.form:
                if user == []:
                    error = 'Cannot find username. Please try again or sign up for account.'
                else:
                    sql_edit('UPDATE USERS SET CONFIRMED = "RESET" WHERE EMAIL = "%s"' % request.form['username'])
                    rtoken = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    sql_edit('UPDATE USERS SET TOKEN = "%s" WHERE EMAIL = "%s"' % (generate_password_hash(rtoken), request.form['username']))
                    send_email(form.username.data, 'Credit Card Data Entry - Reset Password',
                               "Hi %s %s,\n\nTo reset your password, please enter your confimation code provided below into the prompted screen.\n\nConfirmation Code: %s" % (user[0]['NAME_FIRST'], user[0]['NAME_LAST'], rtoken))
                    return redirect(url_for('login.resetpw'))
            else:
                if user == []:
                    error = 'Invalid Credentials. Please try again.'
                elif check_password_hash(user[0]['PASSWORD'], request.form['password']) == False:
                    error = 'Invalid Credentials. Please try again.'
                elif user[0]['CONFIRMED'] != 'TRUE':
                    if user[0]['CONFIRMED'] == 'RESET':
                        error = 'Password must be reset.'
                    else:
                        error = 'Please finish registering account with confirmation code.'
                else:
                    session['logged_in'] = True
                    session['user'] = user[0]['NAME_FIRST'] + ' ' + user[0]['NAME_LAST']
                    session['email'] = request.form['username']
                    session['rights'] = user[0]['RIGHTS']
                    return redirect(url_for('application.home'))
        else:
            return render_template('welcome.html', form=form, error=error)
    return render_template('welcome.html', form=form, error=error)

@login_bp.route('/resetpw/', methods=['GET', 'POST'])
@logged_in_reroute
def resetpw():
    error = None
    form = ForgotPassword()
    if form.validate_on_submit():
        user = sql_pull('SELECT * FROM USERS WHERE EMAIL = "%s"' % request.form['username'])
        if user == []:
            error = 'Invalid Email. Please try again.'
        elif check_password_hash(user[0]['TOKEN'], form.confirmcode.data) == False:
            error = 'Invalid Confirmation Code. Please try again.'
        else:
            sql_edit('''UPDATE USERS SET CONFIRMED = "TRUE" WHERE EMAIL = "%s"''' % form.username.data)
            sql_edit('''UPDATE USERS SET PASSWORD = "%s" WHERE EMAIL = "%s"''' % (generate_password_hash(form.password.data), form.username.data))
            return redirect(url_for('login.welcome'))
    return render_template('resetpassword.html', form=form, error=error)

@login_bp.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login.welcome'))