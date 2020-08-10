from . import db
from flask_user import UserMixin

STATION_REF = None

def prepare_referent(func):
    def wrapper(*args, **kwargs):
        global STATION_REF
        if not STATION_REF:
            STATION_REF = {station.station_id: station.station_name for station in Station.query.all()}
        return func(*args, **kwargs)
    return wrapper

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(
        db.Integer, 
        primary_key=True)
    tracking_number = db.Column(
        db.String(100), 
        index=True,
        nullable=False, 
        unique=True)
    status = db.Column(
        db.Integer, 
        nullable=False, 
        server_default='0')
    created_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=False,
        server_default='Now()')
    customer_department = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    customer_name = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    customer_address = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    employee_name = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    full_cost = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    deposited_cost = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    remaining_cost = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    product_type = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    product_detail = db.Column(
        db.String(100), 
        nullable=True,
        unique=False)
    quantity = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    width = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    height = db.Column(
        db.Integer, 
        nullable=True,
        unique=False)
    due_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=True)

    @prepare_referent
    def get_product_meta(self):
        result = {}
        result['key'] = self.product_id
        result['product_id'] = self.product_id
        if self.status >= 100 and self.status < 200:
            result['status'] = STATION_REF[self.status]
        else:
            result['status'] = self.status
        result['created_date'] = self.created_date.strftime("%d/%m/%Y")
        result['customer_department'] = self.customer_department
        result['customer_name'] = self.customer_name
        result['employee_name'] = self.employee_name
        result['product_type'] = self.product_type
        result['due_date'] = self.due_date.strftime("%d/%m/%Y") if self.due_date else None
        return result

    @prepare_referent
    def get_product_detail(self):
        result = {}
        result['key'] = self.product_id
        result['product_id'] = self.product_id
        result['tracking_number'] = self.tracking_number
        if self.status >= 100 and self.status < 200:
            result['status'] = STATION_REF[self.status]
        else:
            result['status'] = self.status
        result['created_date'] = self.created_date.strftime("%d/%m/%Y - %H:%M:%S")
        result['customer_department'] = self.customer_department
        result['customer_name'] = self.customer_name
        result['customer_address'] = self.customer_address
        result['employee_name'] = self.employee_name
        result['full_cost'] = self.full_cost
        result['deposited_cost'] = self.deposited_cost
        result['remaining_cost'] = self.remaining_cost
        result['product_type'] = self.product_type
        result['product_detail'] = self.product_detail
        result['quantity'] = self.quantity
        result['width'] = self.width
        result['height'] = self.height
        result['due_date'] = self.due_date.strftime("%d/%m/%Y") if self.due_date else None
        return result

class Order(db.Model):
    __tablename__ = 'order'
    product_order_id = db.Column(
        db.Integer, 
        primary_key=True)
    product_id = db.Column(
        db.Integer,
        index=True,
        nullable=False, 
        unique=False)
    station = db.Column(
        db.Integer, 
        nullable=False)
    status = db.Column(
        db.Integer, 
        nullable=False, 
        server_default='0')
    created_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=False,
        server_default='Now()')
    complete_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=True)

    @prepare_referent
    def get_order_detail(self):
        result = {}
        result['key'] = self.product_order_id
        result['product_order_id'] = self.product_order_id
        result['product_id'] = self.product_id
        result['status'] = self.status
        result['station'] = STATION_REF[self.station]
        result['created_date'] = self.created_date.strftime("%d/%m/%Y")
        result['complete_date'] = self.complete_date.strftime("%d/%m/%Y - %H:%M:%S") if self.complete_date else None
        return result

class Status(db.Model):
    __tablename__ = 'status'
    status_id = db.Column(
        db.Integer, 
        primary_key=True)
    meaning = db.Column(
        db.String(100), 
        nullable=False)

class Station(db.Model):
    __tablename__ = 'station'
    station_id = db.Column(
        db.Integer, 
        primary_key=True)
    station_name = db.Column(
        db.String(100), 
        nullable=False)

class Image(db.Model):
    __tablename__ = 'image'
    image_id = db.Column(
        db.Integer, 
        primary_key=True)
    gdrive_id = db.Column(
        db.String(100), 
        nullable=False)
    product_id = db.Column(
        db.Integer,
        index=True,
        nullable=False, 
        unique=False)
    product_order_id = db.Column(
        db.Integer,
        index=True,
        nullable=True, 
        unique=False)
    created_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=False,
        server_default='Now()')
    def get_image_id(self):
        result = {}
        result['key'] = self.image_id
        result['gdrive_id'] = self.gdrive_id
        result['product_id'] = self.product_id
        result['product_order_id'] = self.product_order_id
        return result

class User(db.Model, UserMixin):
    __tablename__ = 'users_data'
    id = db.Column(
        db.Integer, 
        primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
    # User information
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    def __repr__(self):
        return '<User {}>'.format(self.username)