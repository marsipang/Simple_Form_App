import sqlite3
from flask import g

def sql_pull(sqlquery):
    '''Pulls data from the database for the website'''
    g.db = sqlite3.connect("website.db")
    cur = g.db.execute(sqlquery)
    names = [x[0] for x in cur.description]
    dictionary = [dict(zip(names, row)) for row in cur.fetchall()]
    g.db.close()
    return dictionary

def sql_single_field(sqlquery):
    '''When you want a single object pulled from the database. E.g. want just the max insert date'''
    g.db = sqlite3.connect("website.db")
    cur = g.db.execute(sqlquery)
    field = cur.fetchall()[0][0]
    g.db.close()
    return field

def sql_edit(sqlquery):
    '''Creates, alters, deletes, inserts, etc. the database'''
    g.db = sqlite3.connect("website.db")
    g.db.execute(sqlquery)
    g.db.commit()
    g.db.close()
