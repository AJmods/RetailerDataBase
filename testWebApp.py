"""
demo.py

Christopher Jones, 10 Sep 2020

Demo of using flask with Oracle Database
"""
from functools import reduce

import os
import sys
import cx_Oracle
import pandas as pd
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from jinja2 import meta
from sqlalchemy import create_engine

app = Flask(__name__)

DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
USERNAME = os.getenv("SQL_USERNAME") #enter your username
PASSWORD = os.getenv("SQL_PASSWORD") #enter your password
HOST = 'localhost' #enter the oracle db host url
PORT = 1521 # enter the oracle port number
SERVICE = 'orcl' # enter the oracle db service name
ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

engine = create_engine(ENGINE_PATH_WIN_AUTH)

app.config['SQLALCHEMY_DATABASE_URI'] = ENGINE_PATH_WIN_AUTH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    birthDate = db.Column(db.String(20), index=True)
    address = db.Column(db.String(256))
    phoneNumber = db.Column(db.String(20))
    email = db.Column(db.String(120))

    def to_dict(self):
        return {
            'userID': self.userID,
            'name': self.name,
            'birthDate': self.birthDate,
            'address': self.address,
            'phoneNumber': self.phoneNumber,
            'email': self.email
        }

db.create_all()

# Display a welcome message on the 'home' page
@app.route('/')
def index():
    return "Welcome to the app"

@app.route('/Users')
def displayUsers():
    return render_template('UsersTable.html', title='Users Table')
@app.route('/api/data/Users')
def data():
    query = Users.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Users.name.like(f'%{search}%'),
            Users.email.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'email']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Users, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Users.query.count(),
        'draw': request.args.get('draw', type=int),
    }




################################################################################
#
# Initialization is done once at startup time
#
if __name__ == '__main__':
    app.run()
