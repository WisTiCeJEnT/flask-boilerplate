from flask import request, render_template, make_response, jsonify, abort, redirect, url_for
from flask import current_app as app
from .models import db, User, Product, Order, Station, Image
from sqlalchemy import desc

from flask_user import login_required, UserManager, UserMixin
from flask_login import logout_user, login_user
from werkzeug.security import check_password_hash

import traceback
import datetime
import os

import google_drive_api

NUMBER_OF_STATION = 9
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# user_manager = UserManager(app, db, User)

@app.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    tracking_number = datetime.datetime.now()
    check_list = [
        'customer_department', 
        'customer_name',
        'customer_address',
        'employee_name',
        'full_cost',
        'deposited_cost',
        'remaining_cost',
        'product_type',
        'product_detail',
        'quantity',
        'width',
        'height',
        'due_date'
    ]
    for ck in check_list:
        if ck not in data:
            data[ck] = None
    new_product = Product(
        tracking_number = tracking_number,
        customer_department = data['customer_department'],
        customer_name = data['customer_name'],
        customer_address = data['customer_address'],
        employee_name = data['employee_name'],
        full_cost = data['full_cost'],
        deposited_cost = data['deposited_cost'],
        remaining_cost = data['remaining_cost'],
        product_type = data['product_type'],
        product_detail = data['product_detail'],
        quantity = data['quantity'],
        width = data['width'],
        height = data['height'],
        due_date = datetime.datetime(int(data['due_date'][2]), int(data['due_date'][1]), int(data['due_date'][0])) if data['due_date'] else None,
        created_date = datetime.datetime.now(),
    )
    print(new_product.product_id)
    db.session.add(new_product)
    db.session.commit()
    for i in range(NUMBER_OF_STATION):
        if data['order'][i]:
            db.session.add(Order(
                product_id = new_product.product_id,
                station = 100 + i,  #station no start with 100
                status = 200,
                created_date = datetime.datetime.now()
            ))
    db.session.commit()
    return jsonify({
        'tracking_number': str(tracking_number),
        'status': 'ok',
        'product_id': new_product.product_id
    })

@app.route('/api/get_product_list', methods=['GET'])
def get_product_list():
    products = Product.query.order_by(desc(Product.product_id)).all()
    return jsonify({
        'status': 'ok',
        'data': [pd.get_product_meta() for pd in products]
    })

@app.route('/api/get_product_detail', methods=['GET'])
def get_product_detail():
    product = Product.query.get(request.args.get('product_id'))
    product_detail = product.get_product_detail() if product else {}
    timeline = Order.query.filter_by(product_id = request.args.get('product_id')).order_by(Order.complete_date).all()
    tmp = []
    for i in [202, 201, 200]:
        for j in timeline:
            if j.status == i:
                tmp.append(j)
    timeline = tmp
    product_detail['timeline'] = [order.get_order_detail() for order in timeline]
    images = Image.query.filter_by(product_id = request.args.get('product_id')).order_by(desc(Image.image_id)).all()
    product_detail['images'] = [im.get_image_id() for im in images]
    return jsonify({
        'status': 'ok',
        'data': product_detail
    })

@app.route('/api/update_order_status', methods=['POST'])
def update_order_status():
    data = request.json
    order = Order.query.get(data['product_order_id'])
    if not order:
        return abort(400, 'invalid product_order_id')
    order.status = data['status']
    if data['status'] == 201:   #กำลังทำงาน
        product = Product.query.get(order.product_id)
        product.status = order.station
    elif data['status'] == 202: #เสร็จสิ้น
        order.complete_date = datetime.datetime.now()
        product_orders = Order.query.filter_by(product_id = order.product_id).all()
        product = Product.query.get(order.product_id)
        if all([product_order.status == 202 for product_order in product_orders]): #check if all of product's order is complete
            product.status = 2
        elif all([product_order.status != 201 for product_order in product_orders]): #check if none of product's order is working
            product.status = 0
        else:
            product.status = order.station
    db.session.commit()
    return jsonify({
        'status': 'ok',
    })

@app.route('/api/get_station_order', methods=['GET'])
def get_station_order():
    station_id = request.args.get('station_id')
    station_orders = db.session.query(Order, Product).join(Product, Order.product_id==Product.product_id).filter(Order.station == station_id).all()
    result = []
    for order in station_orders:
        tmp = order[0].get_order_detail()
        tmp['product_data'] = order[1].get_product_meta()
        result.append(tmp)
    return jsonify({
        'status': 'ok',
        'data': result,
    })

@app.route('/api/remove_product', methods=['DELETE'])
def delete_product():
    data = request.json
    product = Product.query.get(data['product_id'])
    orders = Order.query.filter_by(product_id = data['product_id']).all()
    imgs = Image.query.filter_by(product_id = data['product_id']).all()
    db.session.delete(product)
    for order in orders:
        db.session.delete(order)
    for img in imgs:
        db.session.delete(img)
    db.session.commit()
    return jsonify({
        'status': 'ok'
    })

@app.route('/img/upload', methods=['POST'])
def upload_image():
    product_id = request.form.get('product_id')
    product_order_id = request.form.get('product_order_id')
    if 'file' in request.files:
        files = request.files.getlist('file')
        for file in files:
            if allowed_file(file.filename):
                filename = file.filename # secure_filename(file.filename)
                # file_path = filename
                # file_path = os.path.join('static/uploads/', filename)
                file_path = product_id + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S")
                file.save(file_path)
                file_id = google_drive_api.upload_file(file_path)
                os.remove(file_path)
                db.session.add(Image(
                    gdrive_id = file_id,
                    product_id = product_id,
                    product_order_id = product_order_id,
                    created_date = datetime.datetime.now()
                ))
        db.session.commit()
    return jsonify({
        'status': 'ok',
    })

@app.route('/img/display')
def display_image():
	return str(os.listdir('static/uploads/'))

@app.route('/ex', methods=['GET'])
def create_user():
    """Create a user."""
    username = request.args.get('user')
    email = request.args.get('email')
    if username and email:
        new_user = User(username=username,
                        password=email)
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
    return make_response(f"{new_user} successfully created!")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        # check if user actually exists
        # take the user supplied password, hash it, and compare it to the hashed password in database

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/login')
        print(user.username)
        login_user(user)
        return redirect('/bof')
    return render_template('login_page.html')

################## BOF Zone ##################

@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect('/')

def try_get(inp, default):
    return inp if inp != None else default

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.engine.execute("SET TIME ZONE 'Asia/Bangkok'")