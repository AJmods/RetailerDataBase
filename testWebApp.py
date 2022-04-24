from wtforms_sqlalchemy.orm import model_form

import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Identity

import cv2
import base64

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
    __tablename__ = "users"
    userID = db.Column(db.Integer(), Identity(start=3), primary_key=True)
    name = db.Column(db.String(64), index=True)
    birthDate = db.Column(db.String(20), index=True)
    address = db.Column(db.String(256))
    phoneNumber = db.Column(db.String(20))
    email = db.Column(db.String(120))

    def to_dict(self):
        print('USERS TO DICT')
        return {
            'userID': self.userID,
            'name': self.name,
            'birthDate': self.birthDate,
            'address': self.address,
            'phoneNumber': self.phoneNumber,
            'email': self.email
        }

UserForm = model_form(Users)

class Products(db.Model):
    __tablename__ = 'products'
    productID = db.Column(db.Integer(), Identity(start=3), primary_key=True)
    name = db.Column(db.String(64), index=True)
    department= db.Column(db.String(20),index=True)
    price=db.Column(db.Float(10,2))
    image = db.Column(db.String(60))

    def to_dict(self):
        print("pRODUCT TO DICT")
        # get image and encode it to base64 to be displayed in table
        try:
            img = cv2.imread(self.image)
            jpg_img = cv2.imencode('.jpg', img)
            b64_string = 'data:image/jpeg;base64,'+ base64.b64encode(jpg_img[1]).decode('utf-8')
            print(b64_string)
        except : # default image if image cannot be found
            b64_string = "data:image/jpeg;base64,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"

        button = f'<input type="submit" name="{self.productID}" value="Add to Cart">'
        print(button)
        return {
            'productID': self.productID,
            'name':self.name,
            'department':self.department,
            'price': f"${self.price}",
            'image': f'<img src="{b64_string}" height=100 width=100/>',
            'button': button}

ProductForm = model_form(Products)

# with engine.connect() as con:
#
#     tableName = 'USERS'
#     rs = con.execute(f'select COLUMN_NAME from SYS.USER_TAB_COLUMNS where TABLE_NAME = {tableName}')
#
#     print('execute work')
#     for row in rs:
#         print(row)

@app.route('/')
def index():
    return "Welcome to the app"

@app.route('/Users',methods=["GET", "POST"])
def displayUsers():

    user = Users()
    success = False

    if request.method == "POST":
        form = UserForm(request.form, obj=user)
        if form.validate():
            form.populate_obj(user)
            db.session.add(user)
            db.session.commit()
            success = True
    else:
        form = UserForm(obj=user)

    #return render_template("create.html", form=form, success=success)

    return render_template('UsersTable.html', title='Users Table', form=form, success=success)
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

@app.route('/Products',methods=["GET", "POST"])
def displayProducts():
    print('method ran')

    product = Products()
    success = False

    if request.method == "POST":
        if request.form['3'] == 'Do Something':
            print('subbmited ducklers')
        else:
            form = ProductForm(request.form, obj=product)
            if form.validate():
                form.populate_obj(product)
                db.session.add(product)
                db.session.commit()
                success = True
    else:
        form = ProductForm(obj=product)

    #return render_template("create.html", form=form, success=success)

    return render_template('ProductsTable.html', title='Products Table', form=form, success=success)
@app.route('/api/data/Products')
def Productdata():
    query = Products.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Products.name.like(f'%{search}%'),
            Products.department.like(f'%{search}%')
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
        if col_name not in ['name', 'department']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Products, col_name)
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
        'data': [product.to_dict() for product in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Products.query.count(),
        'draw': request.args.get('draw', type=int),
    }

################################################################################
#
# Initialization is done once at startup time
#
if __name__ == '__main__':

    db.create_all()

    app.run()
