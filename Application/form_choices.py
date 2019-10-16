# Setting up packages
from sql import sql_pull


def product_opts():
    data = sql_pull('''SELECT PROD_ID, PRODUCT FROM PRODUCT_CODES''')
    choices = [(0, 'Select Choice')] + [(t['PROD_ID'], t['PRODUCT']) for t in data]
    return choices

def country_opts():
    data = sql_pull('''SELECT DISTINCT COUNTRY, COUNTRY_CODE_3 FROM STATE_COUNTRY WHERE COUNTRY_CODE_3 != "USA" AND RISK = "" ORDER BY COUNTRY''')
    choices = [('', 'Select Choice'), ('USA', 'United States of America')] + [(t['COUNTRY_CODE_3'], t['COUNTRY']) for t in data]
    return choices

def state_opts():
    data = sql_pull('''SELECT DISTINCT STATE, STATE_CODE FROM STATE_COUNTRY WHERE STATE_CODE NOT IN ("HI", "MP", "GU") AND STATE IS NOT NULL ORDER BY STATE''')
    choices = [('', 'Select Choice'), ('HI', 'Hawaii'), ('GU', 'Guam'), ('MP', 'Saipan')] + [(t['STATE_CODE'], t['STATE']) for t in data]
    return choices

def employment_opts():
    choices=[('', 'Select Choice'), ('Employed', 'Employed'), ('Self-Employed', 'Self-Employed'), ('Unemployed', 'Unemployed'), ('Retired', 'Retired'), ('Other', 'Other')]
    return choices

def living_opts():
    choices = [('', 'Select Choice'), ('OWN', 'Own'), ('RENT', 'Rent'), ('LWP', 'Live with Relatives'), ('OTHE', 'Other')]
    return choices