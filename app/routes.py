from flask import request, render_template, make_response, jsonify, abort, redirect, url_for
from flask import current_app as app
from .models import db, Product
from sqlalchemy import desc

import traceback
import datetime

@app.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    new_product = Product(
        created_date = datetime.datetime.now(),
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
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

################## BOF Zone ##################

@app.route('/', methods=['GET'])
def bof_root():
    return 'working'

################## Support Zone ##################
def try_get(inp, default):
    return inp if inp != None else default

db.engine.execute("SET TIME ZONE 'Asia/Bangkok'")