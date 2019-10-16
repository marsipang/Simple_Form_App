# Setting up packages
import random, string
from flask import Flask, render_template, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash
from config import Config, send_email, host, login_required
from sql import sql_pull, sql_edit
from Tables.forms import AddUser

app = Flask(__name__)
app.config.from_object(Config)

tables_bp = Blueprint('tables', __name__, template_folder='templates')

@tables_bp.route('/', methods=['GET', 'POST'])
@login_required
def tables():
    return render_template("tables.html")

@tables_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    data = sql_pull('''SELECT NAME_FIRST || " " || NAME_LAST AS FULL_NAME, EMAIL, RIGHTS, INSERT_DTTM FROM USERS''')
    form = AddUser()
    error = None
    if form.validate_on_submit():
        usercheck = sql_pull(f'''SELECT USERID FROM USERS WHERE EMAIL="{form.email.data}"''')
        if usercheck != []:
            error = 'User already exists'
        else:
            rtoken = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            send_email(form.email.data, 'Data Entry Registration',
                       f'''Hi {form.firstname.data} {form.lastname.data},\n\nYou've been registered to use the Credit Card Data Entry website. You'll need to enter the below information into the site {host + 'resetpw'} below to access the site for the first time.\n\nUser ID: {form.userid.data}\nConfirmation Code: {rtoken}''')
            sql_edit(f'''INSERT INTO USERS(NAME_FIRST, NAME_LAST, EMAIL, PASSWORD, RIGHTS, TOKEN, CONFIRMED, INSERT_DTTM) VALUES("{form.firstname.data}", "{form.lastname.data}", "{form.email.data}", "{generate_password_hash('temp')}", "Normal", "{generate_password_hash(rtoken)}", "FALSE", datetime("now", "localtime"))''')
            return redirect(url_for('tables.users'))
    return render_template("users.html", data=data, form=form, error=error, permissions=session['rights'])
   
@tables_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    data = sql_pull('''SELECT * FROM PRODUCT_CODES''')
    return render_template("products.html", data=data)

@tables_bp.route('/statecountry', methods=['GET', 'POST'])
@login_required
def statecountry():
    data = sql_pull('''SELECT * FROM STATE_COUNTRY''')
    return render_template("statecountry.html", data=data)

