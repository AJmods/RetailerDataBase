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
from flask import Flask, render_template

# SET UP THESE ENVIRONMENT VARIABLES BEFORE RUNNING THE PROGRAM
DATABASE_USERNAME = os.getenv("SQL_USERNAME") #username for sql database
DATABASE_PASSWORD = os.getenv("SQL_PASSWORD") #password for sql database
DATABASE_URL = os.getenv('SQL_CONNECT_URL')  # url to connect to database.  If you don't know what to set this varible as, set it to localhost:1521/orcl
PORT = 8080

################################################################################
#
# On macOS tell cx_Oracle 8 where the Instant Client libraries are.  You can do
# the same on Windows, or add the directories to PATH.  On Linux, use ldconfig
# or LD_LIBRARY_PATH.  cx_Oracle installation instructions are at:
# https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html
if sys.platform.startswith("darwin"):
    cx_Oracle.init_oracle_client(lib_dir=os.environ.get("HOME") + "/instantclient_21_3")
elif sys.platform.startswith("win32"):
    cx_Oracle.init_oracle_client(lib_dir=r"c:\oracle\instantclient_21_3")


################################################################################
#
# Start a connection pool.
#
# Connection pools allow multiple, concurrent web requests to be efficiently
# handled.  The alternative would be to open a new connection for each use
# which would be very slow, inefficient, and not scalable.  Connection pools
# support Oracle high availability features.
#
# Doc link: https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html#connection-pooling


# init_session(): a 'session callback' to efficiently set any initial state
# that each connection should have.
#
# If you have multiple SQL statements, then put them all in a PL/SQL anonymous
# block with BEGIN/END so you only call execute() once.  This is shown later in
# create_schema().
#
# This particular demo doesn't use dates, so sessionCallback could be omitted,
# but it does show settings many apps would use.
#
# Note there is no explicit 'close cursor' or 'close connection'.  At the
# end-of-scope when init_session() finishes, the cursor and connection will be
# closed automatically.  In real apps with a bigger code base, you will want to
# close each connection as early as possible so another web request can use it.
#
# Doc link: https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html#session-callbacks-for-setting-pooled-connection-state
#
def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("""
        ALTER SESSION SET
          TIME_ZONE = 'UTC'
          NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI'""")


# start_pool(): starts the connection pool
def start_pool():
    # Generally a fixed-size pool is recommended, i.e. pool_min=pool_max.
    # Here the pool contains 4 connections, which is fine for 4 concurrent
    # users.
    #
    # The "get mode" is chosen so that if all connections are already in use, any
    # subsequent acquire() will wait for one to become available.

    pool_min = 4
    pool_max = 4
    pool_inc = 0
    pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT

    print(f"Connecting to {DATABASE_URL} with username {DATABASE_USERNAME} and password {DATABASE_PASSWORD}")

    pool = cx_Oracle.SessionPool(user=DATABASE_USERNAME,
                                 password=DATABASE_PASSWORD,
                                 dsn=DATABASE_URL,
                                 min=pool_min,
                                 max=pool_max,
                                 increment=pool_inc,
                                 threaded=True,
                                 getmode=pool_gmd,
                                 sessionCallback=init_session)
    print('connected to database')

    return pool


################################################################################
#
# create_schema(): drop and create the demo table, and add a row
#
def create_schema():
    connection = pool.acquire()
    cursor = connection.cursor()
    cursor.execute("""
        begin
          begin
            execute immediate 'drop table Users';
            exception when others then
              if sqlcode <> -942 then
                raise;
              end if;
          end;
          
          execute immediate 'create table Users (
                user_ID      varchar(20) primary key,
                email       varchar(20),
                first_Name   varchar(20),
                last_Name    varchar(20),
                phone_Number varchar(20),
                birth_Date   varchar(20),
                address varchar(20),
                city varchar(20),
                state varchar(2),
                zipcode varchar(10)
            )';
          commit;
        end;""")


################################################################################
#
# Specify some routes
#
# The default route will display a welcome message:
#   http://127.0.0.1:8080/
#
# To insert a new user 'fred' you can call:
#    http://127.0.0.1:8080/post/fred
#
# To find a username you can pass an id, for example 1:
#   http://127.0.0.1:8080/user/1
#

app = Flask(__name__)


# Display a welcome message on the 'home' page
@app.route('/')
def index():
    return "Welcome to the demo app"


@app.route('/users')
def displayUserTable():
    connection = pool.acquire()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Users VALUES ('123','deeznuts@.iit.edu','Robot Downy', 'Syndrome', '6969696969','01-01-70','123 duh wae','Shitcago','IL','42069')")
    return "<html><body>" + '<h1>Panadas table:</h1>' + sqlTableToHTMLPandas(connection, 'users') + '<h1>My table:</h1>'+ sqlTableToHTML(cursor, 'users')+ "</body></html>"

def sqlTableToHTMLPandas(connection, tableName):
    table = pd.read_sql(f'select * from {tableName}', connection)
    s = table.to_html()
    return s
def sqlTableToHTML(cursor, tableName):
    cursor.execute(f"select COLUMN_NAME from SYS.USER_TAB_COLUMNS where TABLE_NAME = '{tableName.upper()}'")
    s = "<table border = '1'>"
    s = s + '<tr>'
    for x in cursor:
        s = s + "<th>" + str(makeTextLookBetter(x[0])) + "</th>"
    s = s + "</tr>"
    cursor.execute(f"SELECT * FROM {tableName}")
    for row in cursor:
        s = s + "<tr>"
    for x in row:
        s = s + "<td>" + str(x) + "</td>"
    s = s + "</tr>"
    print(s)
    return s


def makeTextLookBetter(txt):
    words = txt.split('_')
    newText = ''
    for x in words:
        x = x.capitalize()
        newText += x + ' '
    return newText[:-1]


################################################################################
#
# Initialization is done once at startup time
#
if __name__ == '__main__':
    # Start a pool of connections

    print(os.getenv('PROCESSOR_LEVEL'))
    pool = start_pool()
    print('connected to database')

    # Create a demo table
    create_schema()
    print('created demo table')

    # Start a webserver
    app.run(port=PORT)
