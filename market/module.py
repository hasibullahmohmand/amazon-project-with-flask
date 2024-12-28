from market import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Product(db.Model):
    __tablename__ = 'product'
    uniq_id = db.Column(db.String(length=32), primary_key=True, nullable=False)
    product_name = db.Column(db.String(length=150), unique=True, nullable=False)
    selling_price = db.Column(db.Integer(), nullable=False)
    about_product = db.Column(db.String(length=500), nullable=False)
    image = db.Column(db.String(length=500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_count = db.Column(db.Integer, nullable=False)
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=24), unique=True, nullable=False)
    email = db.Column(db.String(length=50), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=16), nullable=False)
    buget = db.Column(db.Integer, nullable=False, default=10000)
    
    @property
    def password(self):
        return self.password
    @password.setter
    def password(self, palin_password):
        self.password_hash = bcrypt.generate_password_hash(palin_password).decode('utf-8')
        
    def check_password_correction(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=24), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.uniq_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    delivery_date = db.Column(db.Date, nullable=True, default=datetime.now().date()+timedelta(3))
    shipping_cost = db.Column(db.Integer, nullable=True, default=0)
    product = db.relationship('Product', backref='cart')
    
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(length=24), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.uniq_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    delivery_date = db.Column(db.Date, nullable=True, default=datetime.now().date()+timedelta(3))
    order_date = db.Column(db.Date, nullable=True,)
    shipping_cost = db.Column(db.Integer, nullable=True, default=0)
    product = db.relationship('Product', backref='order')
    def __init__(self, **kwargs): 
        super().__init__(**kwargs) 
        self.id = os.urandom(20).hex()
    