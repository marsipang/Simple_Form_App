# -*- coding: utf-8 -*-
"""
Created on Mon May  6 14:34:01 2019

@author: mpang
"""
from datetime import date

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def txt2boolean(field):
    if field.lower() == 'false':
        field = False
    else:
        field = True
    return field
    