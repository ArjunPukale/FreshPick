from .database import db
from flask_login import UserMixin
import datetime
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_name = db.Column(db.String,unique=True, nullable=False ,primary_key=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    phone_number = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String, nullable=False, default="N")#N->Normal, SM->Storemanager
    basket_items = db.relationship('BasketMaster', backref='user')
    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.user_name
    
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer,unique=True, autoincrement=True, primary_key=True)
    category_name = db.Column(db.String,unique=True, nullable=False )
    products = db.relationship('Product', backref='category', lazy='subquery')

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True)
    product_name = db.Column(db.String,  nullable=False )
    product_desc = db.Column(db.String,  nullable=False )
    product_img = db.Column(db.String,  nullable=False )
    product_price_per_unit = db.Column(db.Numeric, nullable=False )
    product_stock = db.Column(db.Integer,  nullable=False )
    product_exp_date = db.Column(db.Date,  nullable=False )
    product_man_date = db.Column(db.Date,  nullable=False )
    product_discount = db.Column(db.Integer,  nullable=False ) #0-100
    veg_nveg = db.Column(db.String,  nullable=False )#V, NV
    category_id = db.Column(db.Integer,   db.ForeignKey("category.category_id"),  nullable=False)#in ForeignKey 1st arg is the name of the class in lowercase
    product_unit = db.Column(db.String)
    product_category = db.relationship("Category",  uselist=False)
class BasketMaster(db.Model):
    __tablename__ = 'basket_master'
    item_id =  db.Column(db.Integer, unique=True, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String, db.ForeignKey("user.user_name"),nullable=False )
    product_id = db.Column(db.Integer,db.ForeignKey("product.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False, default="N")
    product = db.relationship("Product",  uselist=False)

class Orders(db.Model):
    __tablename__ = 'orders'
    item_id =  db.Column(db.Integer,  primary_key=True)
    user_name = db.Column(db.String, db.ForeignKey("user.user_name"),nullable=False )
    product_id = db.Column(db.Integer,db.ForeignKey("product.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    order_price = db.Column(db.Numeric, nullable=False )#price per unit
    order_id = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default="P")#P=Placed, D=Delivered
    address = db.Column(db.String, nullable=False)
    contact_no = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    product = db.relationship("Product",  uselist=False)
    total_price = db.Column(db.Numeric, nullable=False )

#Admin
class AdminReportMaster(db.Model):
    __tablename__ = 'admin_report_master'
    report_id =  db.Column(db.String, unique=True, primary_key=True,nullable=False)
    filename =  db.Column(db.String ,nullable=False)
    report_type =  db.Column(db.String)
    status = db.Column(db.String, nullable=False, default="N")