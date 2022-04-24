import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Identity
from wtforms_sqlalchemy.orm import model_form

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
    userID = db.Column(db.Integer, Identity(start=3), primary_key=True)
    firstName = db.Column(db.String(64), index=True)
    lastName = db.Column(db.String(64), index=True)
    birthDate = db.Column(db.String(20), index=True)
    address = db.Column(db.String(256))
    phoneNumber = db.Column(db.String(20))
    email = db.Column(db.String(120))

    def to_dict(self):
        return {
            'userID': self.userID,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'birthdate': self.birthDate,
            'address': self.address,
            'phoneNumber': self.phoneNumber,
            'email': self.email
        }

db.create_all()

userForm = model_form(Users)

@app.route('/', methods=["GET", "POST"])
def index():
    
    user = Users()
    success = False

    if request.method == "POST":
        form = userForm(request.form, obj=user)
        if form.validate():
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()
            success = True
    else:
        form = userForm(obj=user)

    #return render_template("create.html", form=form, success=success)
    
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
        if col_name not in ['name', 'age', 'email']:
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


if __name__ == '__main__':
    app.run()
