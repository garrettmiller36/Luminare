# -*- coding: utf-8 -*-
"""
    LatexCreator
    
    Create pdf in latex format from a latex template with user's parameters
    
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, request, session, g, redirect, url_for, abort, \
     render_template, flash, current_app
import pandas as pd
from ..models import PARAMETERS
bp = Blueprint('latexcreator', __name__,template_folder='templates')
import datetime
from requests import put, get, post

# def connect_db():
    # """Connects to the specific database."""
    # rv = sqlite3.connect(current_app.config['DATABASE'])
    # rv.row_factory = sqlite3.Row
    # return rv


# def init_db():
    # """Initializes the database."""
    # db = get_db()
    # with current_app.open_resource('schema.sql', mode='r') as f:
        # db.cursor().executescript(f.read())
    # db.commit()


# def get_db():
    # """Opens a new database connection if there is none yet for the
    # current application context.
    # """
    # if not hasattr(g, 'sqlite_db'):
        # g.sqlite_db = connect_db()
    # return g.sqlite_db


@bp.route('/',methods=['GET','POST'])
def show_entries():
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    return render_template('show_entries.html')

# @bp.route('/add', methods=['POST'])
# def add_entry():
    # if not session.get('logged_in'):
        # abort(401)
    # db = get_db()
    # db.execute('insert into entries (title, text) values (?, ?)',
               # [request.form['title'], request.form['text']])
    # db.commit()
    # flash('New entry was successfully posted')
    # return redirect(url_for('latexcreator.show_entries'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('latexcreator.show_entries'))
    return render_template('login.html', error=error)


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('latexcreator.show_entries'))
    

@bp.route('/createpdf',methods=['GET','POST'])
def createpdf():
    response = get('http://localhost:5000/factory_test')
    templates = response.json()['templates']
    return render_template('createpdf.html', templates=templates)
    
@bp.route('/paramentry/<entry>',methods=['GET','POST'])
def paramentry(entry):
    item = entry.split('.tex')[0]
    params = PARAMETERS[item]
    return render_template('paramentry.html',params=params, item=item)

@bp.route('/createdoc/<item>',methods=['GET','POST'])
def createdoc(item):
    test = PARAMETERS
    params = test[item]
    output={}
    for k, v in params.items():
        output[k] = request.form[k]
    output['today']=str(datetime.date.today())
    url = 'http://localhost:5000/factory_test/'+item+'.tex'
    response = post(url,json={'vars': output})
    with open('./static/pdfs/test.pdf', 'wb') as f:
        f.write(response.content)
    file_name = 'test.pdf'
    return redirect(url_for('static', filename='/'.join(['pdfs', file_name])), code=301)

    # return redirect(url_for('latexcreator.show_entries'))
