# Setting up packages
import re, datetime, pandas
from flask import Flask, render_template, redirect, url_for, request, session, Blueprint, jsonify
#from flask.ext.sqlalchemy import SQLAlchemy
from config import Config, login_required
from sql import sql_pull, sql_edit, sql_single_field
from Application.forms import ReviewForm, ApplicationForm, ApplicantForm
from Application.form_choices import product_opts, country_opts, state_opts
from Application.functions import calculate_age, txt2boolean

app = Flask(__name__)
app.config.from_object(Config)
#db = SQLAlchemy(app)

application_bp = Blueprint('application', __name__, template_folder='templates')

@application_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    data = sql_pull('''WITH MAX_DTTM_STATUS AS (SELECT ENTRY_ID, MAX(INSERT_DTTM) AS MAX_DT FROM APP_STATUS_TBL GROUP BY ENTRY_ID)
    SELECT DE.ENTRY_ID, ENTRY_DATE, NAME_FIRST_PRI || " " ||NAME_MIDDLE_PRI || " " || NAME_LAST_PRI || " " || NAME_SUFFIX_PRI AS FULL_NAME, STATUS AS APPSTATUS, AST.INSERT_USER AS OWNER
    FROM DATA_ENTRY DE 
    LEFT JOIN MAX_DTTM_STATUS MDS ON DE.ENTRY_ID=MDS.ENTRY_ID 
    LEFT JOIN APP_STATUS_TBL AST ON DE.ENTRY_ID=AST.ENTRY_ID AND AST.INSERT_DTTM=MAX_DT
    WHERE STATUS IN ("Needs Review")
    ''')
    return render_template("home.html", data=data)

@application_bp.route('/idlestatus', methods=['GET', 'POST'])
@login_required
def idlestatus():
    data = sql_pull('''WITH MAX_DTTM_STATUS AS (SELECT ENTRY_ID, MAX(INSERT_DTTM) AS MAX_DT FROM APP_STATUS_TBL GROUP BY ENTRY_ID)
    SELECT DE.ENTRY_ID, ENTRY_DATE, NAME_FIRST_PRI || " " ||NAME_MIDDLE_PRI || " " || NAME_LAST_PRI || " " || NAME_SUFFIX_PRI AS FULL_NAME, STATUS AS APPSTATUS, AST.INSERT_USER AS OWNER
    FROM DATA_ENTRY DE 
    LEFT JOIN MAX_DTTM_STATUS MDS ON DE.ENTRY_ID=MDS.ENTRY_ID 
    LEFT JOIN APP_STATUS_TBL AST ON DE.ENTRY_ID=AST.ENTRY_ID AND AST.INSERT_DTTM=MAX_DT
    WHERE STATUS NOT IN ("Needs Review")
    ''')
    return render_template("home.html", data=data)

@application_bp.route('/cookie<ENTRY_ID>', methods=['GET', 'POST'])
@login_required
def set_cookie(ENTRY_ID):
    session['ENTRY_ID'] = ENTRY_ID
    return redirect(url_for('application.Review'))
    
@application_bp.route('/<input_type>/base', methods=['GET', 'POST'])
@login_required
def ApplicationBase(input_type):
    if input_type in ['new', 'edit']:
        next
    else:
        return redirect(url_for('application.home'))
    #set form & cookies
    error = None
    form = ApplicationForm()
    form.Product.choices = product_opts()
    if input_type == 'new':
        session['ENTRY_ID'] = ''
    else:
        next
    if form.validate_on_submit():
        if form.dtreceived.data > datetime.date.today():
            error = "The date received can't be greater than today's date"
        else:
            prodcodes = sql_pull(f'''SELECT * FROM PRODUCT_CODES WHERE PROD_ID = {form.Product.data}''')[0]
            if input_type == 'new':
                maxappno = sql_single_field('''SELECT MAX(CAST(REPLACE(ENTRY_ID, 'PAPER_', '') AS INTEGER)) FROM DATA_ENTRY''')
                if maxappno == None:
                    ENTRY_ID = 'APPID_1'
                else:
                    ENTRY_ID = 'APPID_' + str(maxappno + 1)
                session['ENTRY_ID'] = ENTRY_ID
                sql_edit(f'''INSERT INTO DATA_ENTRY(ENTRY_ID, ENTRY_DATE, PRODUCT, INSERT_DTTM, INSERT_USER) 
                            VALUES("{ENTRY_ID}", "{form.dtreceived.data}", "{prodcodes['PRODUCT']}",   
                            datetime("now", "localtime"), "{session['user']}")''')
                sql_edit(f'''INSERT INTO APP_STATUS_TBL(ENTRY_ID, INSERT_DTTM, STATUS, INSERT_USER) VALUES("{ENTRY_ID}", datetime("now", "localtime"), "Needs Review", "{session['user']}")''')
                tableinfo = sql_pull('''PRAGMA table_info(DATA_ENTRY)''')
                nonnullable = [t['name'] for t in tableinfo if t['notnull'] == 0]
                for col in nonnullable:
                    sql_edit(f'''UPDATE DATA_ENTRY SET {col}="" WHERE ENTRY_ID="{ENTRY_ID}" AND {col} IS NULL''')
                return redirect(url_for('application.Applicant', input_type='new'))
            elif input_type == 'edit':
                sql_edit(f'''UPDATE DATA_ENTRY SET ENTRY_DATE="{form.dtreceived.data}", PRODUCT="{prodcodes['PRODUCT']}", 
                          WHERE ENTRY_ID="{session['ENTRY_ID']}"''')
                return redirect(url_for('application.Review'))
            else:
                error = 'Unknown input type'
            
    return render_template("base_input.html", form=form, error=error, entry_id=session['ENTRY_ID'], input_type=input_type)

@application_bp.route('/<input_type>/applicant', methods=['GET', 'POST'])
@login_required
def Applicant(input_type):
    if input_type in ['new', 'edit']:
        next
    else:
        return redirect(url_for('application.home'))
    #set form & cookies
    error = None
    form = ApplicantForm()
    form.StCountry.choices = form.MailCountry.choices =country_opts()
    form.StState.choices = form.MailState.choices = state_opts()
    if form.validate_on_submit():
        if (len(re.sub('[^0-9]', '', form.CellPhone.data)) < 10) & (len(re.sub('[^0-9]', '', form.HomePhone.data)) < 10) & (len(re.sub('[^0-9]', '', form.WorkPhone.data)) < 10):
            error = "At least one valid phone number is required"
        elif (form.DOB.data > datetime.date.today()):
            error = "Date of birth is greater than current date"
        elif (calculate_age(form.DOB.data) < 18):
            error = "Age of primary applicant is less than 18 years"
        elif len(form.FirstName.data + ' ' + form.MiddleName.data + '*' + form.LastName.data) > 36:
            error = "Together, the first, middle, and last name cannot be more than 36 characters long."
        else:
            if form.AddrBoo.data == True:
                mailaddr1 = form.MailAddress1.data
                mailaddr2 = form.MailAddress2.data
                mailcity = form.MailCity.data
                mailctry = form.MailCountry.data
                mailst = form.MailState.data
                mailzip = form.MailZip.data
            else:
                mailaddr1 = form.StAddress1.data
                mailaddr2 = form.StAddress2.data
                mailcity = form.StCity.data
                mailctry = form.StCountry.data
                mailst = form.StState.data
                mailzip = form.StZip.data
            if form.NonTax.data == False:
                form.NonTaxIncome.data = 0
            else:
                next
            sql_edit(f'''UPDATE DATA_ENTRY SET NAME_FIRST_PRI="{form.FirstName.data}", NAME_MIDDLE_PRI="{form.MiddleName.data}", NAME_LAST_PRI="{form.LastName.data}", 
                     NAME_SUFFIX_PRI="{form.Suffix.data}", DOB_PRI="{form.DOB.data}", EMAIL_PRI="{form.Email.data}", STREET_ADDRESS1_PRI="{form.StAddress1.data}", 
                     STREET_ADDRESS2_PRI="{form.StAddress2.data}", STREET_CITY_PRI="{form.StCity.data}", STREET_COUNTRY_PRI="{form.StCountry.data}", STREET_STATE_PRI="{form.StState.data}", 
                     STREET_ZIP_PRI="{form.StZip.data}", MAIL_ADDRESS1_PRI="{mailaddr1}", MAIL_ADDRESS2_PRI="{mailaddr2}", MAIL_CITY_PRI="{mailcity}", MAIL_COUNTRY_PRI="{mailctry}", 
                     MAIL_STATE_PRI="{mailst}", MAIL_ZIP_PRI="{mailzip}", MOBILE_PHONE_PRI="{form.CellPhone.data}", HOME_PHONE_PRI="{form.HomePhone.data}", WORK_PHONE_PRI="{form.WorkPhone.data}", 
                     EMPLOYMENT_STATUS_PRI="{form.EmploymentSt.data}", EMPLOYER_PRI="{form.Employer.data}", OCCUPATION_PRI="{form.Occupation.data}", INCOME_PRI={form.Income.data}, 
                     NON_TAX_INCOME_PRI={form.NonTaxIncome.data}, RESIDENTIAL_STATUS_PRI="{form.ResidentialSt.data}", RENT_PRI={form.Rent.data} WHERE ENTRY_ID="{session['ENTRY_ID']}"''')
            if input_type == 'new':
               return redirect(url_for('application.CoappQuestion', input_type='new'))
            elif input_type == 'edit':
               return redirect(url_for('application.Review'))
            else:
                error = 'Unknown input type'
    return render_template("applicant_input.html", form=form, error=error, title='Applicant Information', entry_id=session['ENTRY_ID'], input_type=input_type)

@application_bp.route('/new/coappquestion', methods=['GET', 'POST'])
@login_required
def CoappQuestion():
    if (request.method == 'POST'):
        if 'Yes' in request.form:
            return redirect(url_for('application.Coapp', input_type='new'))
        else:
            sql_edit(f'''UPDATE DATA_ENTRY SET NAME_FIRST_SEC="", NAME_MIDDLE_SEC="", NAME_LAST_SEC="", NAME_SUFFIX_SEC="", DOB_SEC="", EMAIL_SEC="", STREET_ADDRESS1_SEC="", 
                     STREET_ADDRESS2_SEC="", STREET_CITY_SEC="", STREET_COUNTRY_SEC="", STREET_STATE_SEC="", STREET_ZIP_SEC="", MAIL_ADDRESS1_SEC="", MAIL_ADDRESS2_SEC="", MAIL_CITY_SEC="", MAIL_COUNTRY_SEC="", 
                     MAIL_STATE_SEC="", MAIL_ZIP_SEC="", MOBILE_PHONE_SEC="", HOME_PHONE_SEC="", WORK_PHONE_SEC="", EMPLOYMENT_STATUS_SEC="", EMPLOYER_SEC="", OCCUPATION_SEC="", INCOME_SEC="", 
                     NON_TAX_INCOME_SEC="", RESIDENTIAL_STATUS_SEC="", RENT_SEC="" WHERE ENTRY_ID="{session['ENTRY_ID']}"''')
            return redirect(url_for('application.Review', input_type='new'))
    else:
        next
    return render_template("coapp_question.html", entry_id=session['ENTRY_ID'])

@application_bp.route('/<input_type>/coapp', methods=['GET', 'POST'])
@login_required
def Coapp(input_type):
    if input_type in ['new', 'edit']:
        next
    else:
        return redirect(url_for('application.home'))
    #set form & cookies
    error = None
    form = ApplicantForm()
    form.StCountry.choices = form.MailCountry.choices =country_opts()
    form.StState.choices = form.MailState.choices = state_opts()
    if form.validate_on_submit():
        if (len(re.sub('[^0-9]', '', form.CellPhone.data)) < 10) & (len(re.sub('[^0-9]', '', form.HomePhone.data)) < 10) & (len(re.sub('[^0-9]', '', form.WorkPhone.data)) < 10):
            error = "At least one valid phone number is required"
        elif (form.DOB.data > datetime.date.today()):
            error = "Date of birth is greater than current date"
        elif len(form.FirstName.data + ' ' + form.MiddleName.data + '*' + form.LastName.data) > 36:
            error = "Together, the first, middle, and last name cannot be more than 36 characters long."
        else:
            if form.AddrBoo.data == True:
                mailaddr1 = form.MailAddress1.data
                mailaddr2 = form.MailAddress2.data
                mailcity = form.MailCity.data
                mailctry = form.MailCountry.data
                mailst = form.MailState.data
                mailzip = form.MailZip.data
            else:
                mailaddr1 = form.StAddress1.data
                mailaddr2 = form.StAddress2.data
                mailcity = form.StCity.data
                mailctry = form.StCountry.data
                mailst = form.StState.data
                mailzip = form.StZip.data
            if form.NonTax.data == False:
                form.NonTaxIncome.data = 0
            else:
                next
            sql_edit(f'''UPDATE DATA_ENTRY SET NAME_FIRST_SEC="{form.FirstName.data}", NAME_MIDDLE_SEC="{form.MiddleName.data}", NAME_LAST_SEC="{form.LastName.data}", 
                     NAME_SUFFIX_SEC="{form.Suffix.data}", DOB_SEC="{form.DOB.data}", EMAIL_SEC="{form.Email.data}", STREET_ADDRESS1_SEC="{form.StAddress1.data}", 
                     STREET_ADDRESS2_SEC="{form.StAddress2.data}", STREET_CITY_SEC="{form.StCity.data}", STREET_COUNTRY_SEC="{form.StCountry.data}", STREET_STATE_SEC="{form.StState.data}", 
                     STREET_ZIP_SEC="{form.StZip.data}", MAIL_ADDRESS1_SEC="{mailaddr1}", MAIL_ADDRESS2_SEC="{mailaddr2}", MAIL_CITY_SEC="{mailcity}", MAIL_COUNTRY_SEC="{mailctry}", 
                     MAIL_STATE_SEC="{mailst}", MAIL_ZIP_SEC="{mailzip}", MOBILE_PHONE_SEC="{form.CellPhone.data}", HOME_PHONE_SEC="{form.HomePhone.data}", WORK_PHONE_SEC="{form.WorkPhone.data}", 
                     EMPLOYMENT_STATUS_SEC="{form.EmploymentSt.data}", EMPLOYER_SEC="{form.Employer.data}", OCCUPATION_SEC="{form.Occupation.data}", INCOME_SEC={form.Income.data}, 
                     NON_TAX_INCOME_SEC={form.NonTaxIncome.data}, RESIDENTIAL_STATUS_SEC="{form.ResidentialSt.data}", RENT_SEC={form.Rent.data} WHERE ENTRY_ID="{session['ENTRY_ID']}"''')
            if input_type == 'new':
               return redirect(url_for('application.Branch', input_type='new'))
            elif input_type == 'edit':
               return redirect(url_for('application.Review'))
            else:
                error = 'Unknown input type'
    return render_template("applicant_input.html", form=form, error=error, title='Co-Applicant Information', entry_id=session['ENTRY_ID'], input_type=input_type)

@application_bp.route('/review', methods=['GET', 'POST'])
@login_required
def Review():
    data = sql_pull(f'''SELECT * FROM DATA_ENTRY WHERE ENTRY_ID = "{session['ENTRY_ID']}"''')[0]
    status = sql_single_field(f'''WITH MAX_DT_TBL AS (SELECT ENTRY_ID, MAX(INSERT_DTTM) AS MAX_DT FROM APP_STATUS_TBL WHERE ENTRY_ID = "{session['ENTRY_ID']}")
    SELECT STATUS FROM APP_STATUS_TBL AST LEFT JOIN MAX_DT_TBL MDT ON AST.ENTRY_ID=MDT.ENTRY_ID WHERE AST.ENTRY_ID = "{session['ENTRY_ID']}" AND INSERT_DTTM=MAX_DT''')
    #too lazy to not do select *, so I'm reformatting dates in python instead
    data['ENTRY_DATE'] = datetime.datetime.strptime(data['ENTRY_DATE'], '%Y-%m-%d').strftime('%m/%d/%Y')
    if pandas.notnull(data['DOB_PRI']) and data['DOB_PRI'] != "":
        data['DOB_PRI'] = datetime.datetime.strptime(data['DOB_PRI'], '%Y-%m-%d').strftime('%m/%d/%Y')
    if pandas.notnull(data['DOB_SEC']) and data['DOB_SEC'] != '':
        data['DOB_SEC'] = datetime.datetime.strptime(data['DOB_SEC'], '%Y-%m-%d').strftime('%m/%d/%Y')
    form = ReviewForm()
    error = None
    if form.validate_on_submit():
        if data['NAME_LAST_PRI'] == '':
            error = '''Applicant information isn't filled out'''
        elif status not in ['Upload Error - Needs Review', 'Needs Review']:
            error = '''Cannot Edit due to Status'''
        else:
            sql_edit(f'''INSERT INTO APP_STATUS_TBL(ENTRY_ID, INSERT_DTTM, STATUS, INSERT_USER) VALUES("{session['ENTRY_ID']}", datetime("now", "localtime"), "Reviewed", "{session['user']}")''')
            return redirect(url_for('application.home'))
    return render_template('app_review.html', status=status, data=data, form=form, error=error)

@login_required
@application_bp.route('/prefill/<ENTRY_ID>', methods=['GET', 'POST'])
def job_prefill(ENTRY_ID):
    app = sql_pull(f'''SELECT * FROM DATA_ENTRY WHERE ENTRY_ID = "{session['ENTRY_ID']}"''')[0]
    prodid = {'PROD_ID':sql_single_field(f'''SELECT PROD_ID FROM PRODUCT_CODES WHERE PRODUCT = "{app['PRODUCT']}"''')}
    app = {**app, **prodid}
    if app['CHECKING_ACCT1'] + app['CHECKING_ACCT2'] + app['SAVINGS_ACCT1'] + app['SAVINGS_ACCT2'] != '':
        atm = {'ATM':True}
    else:
        atm = {'ATM':False}
    app = {**app,  **atm}
    if app['STREET_ADDRESS1_PRI'] + app['STREET_ADDRESS2_PRI'] != app['MAIL_ADDRESS1_PRI'] + app['MAIL_ADDRESS2_PRI']:
        mlflgp = {'MLFLG_PRI': True}
    else:
        mlflgp = {'MLFLG_PRI': False}
    app = {**app, **mlflgp}
    if app['NON_TAX_INCOME_PRI'] > 0:
        taxflgp = {'TAX_FLG_PRI': True}
    else:
        taxflgp = {'TAX_FLG_PRI': False}
    app = {**app, **taxflgp}
    if pandas.notnull(app['NAME_LAST_SEC']):
        if app['STREET_ADDRESS1_SEC'] + app['STREET_ADDRESS2_SEC'] != app['MAIL_ADDRESS1_SEC'] + app['MAIL_ADDRESS2_SEC']:
            mlflgs = {'MLFLG_SEC': True}
        else:
            mlflgs = {'MLFLG_SEC': False}
    else:
        mlflgs = {'MLFLG_SEC': False}
    app = {**app, **mlflgs}
    if pandas.notnull(app['NON_TAX_INCOME_SEC']) and app['NON_TAX_INCOME_SEC'] != '':
        if app['NON_TAX_INCOME_SEC'] > 0:
            taxflgs = {'TAX_FLG_SEC': True}
        else:
            taxflgs = {'TAX_FLG_SEC': False}
    else:
        taxflgs = {'TAX_FLG_SEC': False}
    app = {**app, **taxflgs}
    return jsonify(app)