from . import db

STATION_REF = None

def prepare_referent(func):
    def wrapper(*args, **kwargs):
        global STATION_REF
        if not STATION_REF:
            STATION_REF = None
            # STATION_REF = {station.station_id: station.station_name for station in Station.query.all()}
        return func(*args, **kwargs)
    return wrapper

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(
        db.Integer, 
        primary_key=True)
    status = db.Column(
        db.Integer, 
        nullable=False, 
        server_default='0')
    created_date = db.Column(
        db.DateTime,
        unique=False,
        nullable=False,
        server_default='Now()')

    @prepare_referent
    def get_product_meta(self):
        result = {}
        result['key'] = self.product_id
        result['product_id'] = self.product_id
        result['created_date'] = self.created_date.strftime("%d/%m/%Y") if self.created_date else None
        return result