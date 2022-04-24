import os
import random
import sys
from faker import Faker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from testWebApp import Users

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


def create_fake_users(n):
    """Generate fake users."""
    faker = Faker()
    for i in range(n):
        user = Users(email=faker.email(),
                     name=faker.name(),
                     birthDate=faker.date_between(start_date="-80y",end_date="-18y"),
                    address=faker.address().replace('\n', ', '),
                    phoneNumber=faker.phone_number()[:20])
        db.session.add(user)
    db.session.commit()
    print(f'Added {n} fake users to the database.')


if __name__ == '__main__':
    #if len(sys.argv) <= 1:
        #print('Pass the number of users you want to create as an argument.')
       # sys.exit(1)
    create_fake_users(100)
