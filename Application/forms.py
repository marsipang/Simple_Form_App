#Define packages
from flask_wtf import FlaskForm
from wtforms import BooleanField, TextField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from Application.form_choices import employment_opts, living_opts
from regular_expressions import name_permissable, num_permissable, date_permissable, alphanum_permissable, alpha_permissable
import datetime


class RequiredIfTrue(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('RequiredIfTrue',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data in [True, 'Yes', 'USA']:
            super(RequiredIfTrue, self).__call__(form, field)     

class ApplicationForm(FlaskForm):
    dtreceived = DateField('Date Received:', default=datetime.date.today)
    Product = SelectField('Product:', validators=[DataRequired()], coerce=int)

class ApplicantForm(FlaskForm):
    FirstName = TextField('First Name:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=36)], widget=TextArea())
    MiddleName = TextField('Middle Name:', widget=TextArea())
    LastName = TextField('Last Name:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=36)], widget=TextArea())
    Suffix = TextField('Suffix:', widget=TextArea())
    DOB = DateField('Date of Birth:', validators=[DataRequired()])
    Email = TextField('Email Address', widget=TextArea())
    StAddress1 = TextField('Street Address Line 1 (No P.O. Box):', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=40)], widget=TextArea())
    StAddress2 = TextField('Street Address Line 2 (No P.O. Box):', widget=TextArea())
    StCity = TextField('City:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=19)], widget=TextArea())
    StCountry = SelectField('Country:', validators=[DataRequired(), Optional(strip_whitespace=True)])
    StState = SelectField('State:', validators=[RequiredIfTrue('StCountry'), Regexp(alpha_permissable)])
    StZip = TextField('Zip Code:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=0, max=13), Regexp(num_permissable)], widget=TextArea())
    AddrBoo = BooleanField('Check if Mailing Address is different:')
    MailAddress1 = TextField('Mailing Address Line 1:', validators=[RequiredIfTrue('AddrBoo'), Optional(strip_whitespace=True), Length(min=1, max=40)], widget=TextArea())
    MailAddress2 = TextField('Mailing Address Line 2:', widget=TextArea())
    MailCity = TextField('City:', validators=[RequiredIfTrue('AddrBoo'), Optional(strip_whitespace=True), Length(min=1, max=19)], widget=TextArea())
    MailCountry = SelectField('Country:', validators=[RequiredIfTrue('AddrBoo'), Optional(strip_whitespace=True), Length(min=1, max=3), Regexp(alpha_permissable)])
    MailState = SelectField('State:', validators=[RequiredIfTrue('MailCountry'), Regexp(alpha_permissable)])
    MailZip = TextField('Zip Code:', validators=[RequiredIfTrue('AddrBoo'), Optional(strip_whitespace=True), Length(min=0, max=13), Regexp(num_permissable)], widget=TextArea())
    CellPhone = TextField('Mobile Phone Number:')
    HomePhone = TextField('Home Phone Number:')
    WorkPhone = TextField('Work Phone Number:')
    EmploymentSt = SelectField('Employment Status:', validators=[DataRequired()], choices=employment_opts())
    Employer = TextField('Name of Employer/Business:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=36)])
    Occupation = TextField('Occupation/Position:', validators=[DataRequired(), Optional(strip_whitespace=True), Length(min=1, max=10)])
    Income = DecimalField('Total Annual Income:')
    NonTax = SelectField('Is any of income non-taxable?:', validators=[DataRequired()], choices=[('', 'Select choice'), ('Y', 'Yes'), ('N', 'No')])
    NonTaxIncome = DecimalField('How much of annual income is non-taxable?:')
    ResidentialSt = SelectField('Residential Status:',validators=[DataRequired()], choices=living_opts())
    Rent = DecimalField('Monthly Rent/Mortgage Payment:')
      
class ReviewForm(FlaskForm):    
    Reviewed = BooleanField('By checking this box, I confirm that all data above is accurate and I have reviewed the application for completeness(all signatures were received, all required fields filled out, etc.)', validators=[DataRequired()])