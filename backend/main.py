import os
from decimal import Decimal
from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
#from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
# import secrets
from werkzeug.utils import secure_filename
import uuid
import datetime
from datetime import datetime, timedelta
import random
#from flask_sqlalchemy_session import flask_scoped_session
from application.models import *
from application.database import db
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from application.masterdata import MasterData
#celery
from application import workers , tasks
from celery.schedules import crontab
#mail
from flask_mail import Mail, Message

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "grocery_store.sqlite3") 
#"sqlite:///week7_database.sqlite3"
app.config['SECRET_KEY'] = 'thisisasecretkey'
#for jwt token (key)
app.config["JWT_SECRET_KEY"] = "9ed777f3-29a9-487f-a252-0d89e084baf4" #generated using uuid.uuid4()
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['PROPAGATE_EXCEPTIONS'] = True
# mail configurations
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'arjunpukale@gmail.com'
app.config['MAIL_PASSWORD'] = 'wanj ldin svty ujcf'

#db = SQLAlchemy()
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)
#mail
mail  = Mail(app)
#to handle imae upload
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(current_dir, 'static/images')
# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)
# patch_request_class(app)


api = Api(app)
CORS(app)
#celery
app.config['CELERY_BROKER_URL'] = "redis://localhost:6379/1"
app.config['CELERY_RESULT_BACKEND'] = "redis://localhost:6379/2"

celery = workers.celery

celery.conf.update(
    broker_url = app.config["CELERY_BROKER_URL"],
    result_backend = app.config["CELERY_RESULT_BACKEND"],
    timezone='Asia/Kolkata',  # Setting it to Indian timezone
    beat_schedule={
        'run-every-miute': {
            'task': 'application.tasks.print_current_time_job',
            'schedule': crontab(minute='*/1'),#crontab(hour=16, minute=0),  # 4 PM
        },
        'run-every-day-at-4pm': {
            'task': 'application.tasks.send_mail_no_orders_today',
            'schedule': crontab(hour=16, minute=0),  # 4 PM
        },
        'run-every-month-on-28': {
            'task': 'application.tasks.send_order_report',
            'schedule': crontab(day_of_month=28, hour=0, minute=0),  # Midnight on the 25th
        }
    },
)

celery.Task = workers.ContextTask
app.app_context().push()

#engine=db.create_engine("sqlite:///" + os.path.join(current_dir, "database.sqlite3"))
#engine = db.create_engine("sqlite:///database.sqlite3")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_name):
    return User.query.get(user_name)

########## Helper Functions ##########
def discountedPrice(ogPrice, discount):
    #print(ogPrice, type(ogPrice), discount, type(discount))
    return ogPrice*(Decimal(1) - discount*Decimal(0.01))

def getOGPrice(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        ogPrice =  product.product_price_per_unit
        #discount = product.product_discount
        return ogPrice
    else:
        return None
def getDiscount(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        #ogPrice =  product.product_price_per_unit
        discount = product.product_discount
        return discount#discountedPrice(ogPrice,discount)
    else:
        return None

def generate_unique_filename(filename):
    _, ext = os.path.splitext(filename)
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename

def getStockQty(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        stock =  product.product_stock
        
        return stock
    else:
        return None
def generate_order_id():
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M%S%f")  # Format: YYYYMMDDHHMMSSffffff
    random_number = random.randint(1000, 9999)  # Generate a random 4-digit number
    
    order_id = f"{timestamp}{random_number}"
    return order_id
def deleteProductTraces(productId):
    try:
        #first delete basket items of this product
        basketItems = BasketMaster.query.filter_by(product_id=productId).all()
        for basketItem in basketItems:
            db.session.delete(basketItem)

        #delete order entries of this product
        orderItems = Orders.query.filter_by(product_id=productId).all()
        for orderItem in orderItems:
            db.session.delete(orderItem)

        db.session.commit()
        return True
    except Exception as e:
        print(e)
        db.session.rollback()
        return False
#########################################################################
class LoginForm(FlaskForm):
    username = EmailField(validators=[
                           InputRequired()], render_kw={"placeholder": "Email Address"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=5, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = EmailField(validators=[
                           InputRequired()], render_kw={"placeholder": "Email Address"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=5, max=20)], render_kw={"placeholder": "Password"})
    firstName = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "eg: John"})
    lastName = StringField(validators=[
                           ], render_kw={"placeholder": "eg: Cena"})
    phoneNumber = StringField(validators=[InputRequired(),Length(min=10, max=12)
                           ], render_kw={"placeholder": "eg: 906412358"})
    address = TextAreaField(validators=[Length(max=250)
                           ], render_kw={"placeholder": "Enter your complete address"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            user_name=username.data).first()
        if existing_user_username:
            flash("That username already exists. Please choose a different one.")
            raise ValidationError(
                'That username already exists. Please choose a different one.')
##########################################################################



#Creating Category cache ###################
 #fetch list of categories:
categories_master = Category.query.all()
print("# categories: ",len(categories_master))
for category in categories_master:
    print(category.category_name,"#products: ",len(category.products))

#############################################
# MASTERDATA
MasterData.loadCategoryData()
#############################################
job = tasks.send_mail_no_orders_today.delay()
print("send_mail_no_orders_today job :: ",job)

job = tasks.send_order_report.delay()
print("send_order_report job :: ",job)

#####################################
# Fetch user's who have not placed any orders today
# First, get the list of users who have placed orders today
# try:
#     today = datetime.now().date()  # Get the current date
#     orders_today = Orders.query.filter(Orders.created_at >= today).all()
#     print("orders_today::length::", len(orders_today))

#     # Now, let's get the list of all users
#     all_users = User.query.all()

#     # Find the users who haven't placed any orders today
#     users_without_orders_today = [user.user_name for user in all_users if user.user_name not in [order.user_name for order in orders_today]]
#     print("users_without_orders_today::", users_without_orders_today)

#     recipients = ['arjunpukale@gmail.com']
#     subject='flask app mail test'
#     body = "This is the plain text content of the email."

#     message = Message(subject=subject, recipients=recipients, body=body, sender='arjunpukale@gmail.com')
#     mail.send(message)
# except Exception as e:
#     print(e)
######################################
@app.route("/login", methods=["GET", "POST"])
def login():
    print("Inside Login route")
    form = LoginForm()
    if form.validate_on_submit():
        print("form.validate_on_submit()")
        user = User.query.filter_by(user_name=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                print("password matched")
                login_user(user)
                return redirect(url_for('home'))
            print("password did not matched")
            flash("Incorrect Password, Please try again.")
        print("user does not exists")
    print("not form.validate_on_submit()")
    return render_template('login.html', form=form)
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.username.data).first()
        if user:
            flash("User already exists !")
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(user_name=form.username.data, password=hashed_password,
                first_name = str(form.firstName.data).upper(),
                last_name = str(form.lastName.data).upper(),
                phone_number = form.phoneNumber.data,
                address = form.address.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html", form = form)
    

# Default route, redirects to the login route
@app.route("/")
def default_route():
    return redirect(url_for("login"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    print("Inside Home")
    print("Logged in user:: ",current_user.first_name)
    #return "Welcome "+current_user.first_name

    categoryId = request.args.get("categoryId")
    print("categoryId:: ",categoryId) 
    if(not categoryId):
        return render_template("home.html", current_user=current_user, categories=categories_master, discountedPrice = discountedPrice ,getOGPrice=getOGPrice, getDiscount=getDiscount, getStockQty=getStockQty)
    elif(categoryId != ""):
        categories = Category.query.filter_by(category_id = categoryId).all()
        if(len(categories)>0):
            searchCat = True
            return render_template("home.html", current_user=current_user,searchCat=searchCat, categories=categories, discountedPrice = discountedPrice ,getOGPrice=getOGPrice, getDiscount=getDiscount, getStockQty=getStockQty)
    
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    noData = False
    print("Inside search")
    print("Logged in user:: ",current_user.first_name)
    if request.method == "POST":
        
        search_query = request.form.get('query')
        categoryId = request.form.get('category')
        price_range = request.form.get('priceRangeValues')
        min_discount = request.form.get('minDiscountValue')
        veg_nonveg = request.form.get('vegNonveg')
        min_price = None
        max_price = None
        # Process price_range value
        if(price_range!="" and price_range!=None):
            price_range = price_range.replace('₹', '')
            min_price, max_price = price_range.split(' - ')
            min_price = float(min_price)
            max_price = float(max_price)

        if(min_discount!="" and min_discount!=None):
            min_discount = min_discount.replace('%','')

        print("searching for: ",search_query)
        print("searching for categoryId: ",categoryId)
        print("price_range: ",price_range)
        print("min_discount: ",min_discount)
        print("veg_nonveg: ",veg_nonveg)

        if(search_query == "" or search_query == None):
            search_query = ""
        query = Product.query.filter(Product.product_name.like(f"%{search_query}%"))
        if categoryId and categoryId != "":
            query = query.filter(Product.category_id == categoryId)
        if veg_nonveg!=None and veg_nonveg != "":
            query = query.filter(Product.veg_nveg == veg_nonveg)
        if min_price!=None and min_price!="":
            query = query.filter(Product.product_price_per_unit >= float(min_price))
        if max_price!=None and max_price!="" :
            query = query.filter(Product.product_price_per_unit <= float(max_price))
        if min_discount!=None and min_discount!="" :
            query = query.filter(Product.product_discount >= float(min_discount))
        query = query.order_by(Product.product_man_date.desc())  # Sorting by manufacturing date
        products = query.all()
        if(len(products)==0):
            noData = True


        return render_template("search1.html", search_query=search_query, noData=noData,current_user=current_user,categories_master=categories_master, products=products, discountedPrice = discountedPrice ,getOGPrice=getOGPrice, getDiscount=getDiscount, getStockQty=getStockQty)


@app.route('/addToBasket', methods=['POST', 'GET'])
def addToBasket():
  if request.method == "POST":
    basketData = request.get_json()
    print("add to basket: ",basketData)
    user_name = basketData.get("username")
    productId = basketData.get("productId")
    qty = basketData.get("quantity")
    #check if the product already exists in user's basket
    basketItem = BasketMaster.query.filter_by(user_name=user_name, product_id=productId).first()
    if(basketItem):
        results = {'code': 'D'}#duplicate
    else:
        if(getStockQty(productId)<qty):
            results = {'code': 'O',
                       'availQTY':getStockQty(productId)
                       }#out of stock
        
        else:
            try:
                basketItem = BasketMaster(user_name=user_name, product_id=productId,qty=qty )
                db.session.add(basketItem)
                db.session.commit()
                results = {'code': 'S'}#success
            except Exception as e:
                print(e)
                results = {'code': 'F'}#failure
        
  return jsonify(results)

@app.route('/deleteFromBasket', methods=['POST'])
@login_required
def deleteFromBasket():
  if (request.method == "POST" and current_user.first_name):
    basketData = request.get_json()
    print("Inside deleteFromBasket: ",current_user.first_name)
    itemId = basketData.get("itemId")
    #check if the product already exists in user's basket
    basketItem = BasketMaster.query.filter_by(user_name=current_user.user_name, item_id=itemId).first()
    if(basketItem):
        try:
            db.session.delete(basketItem)
            db.session.commit()
            results = {'code': 'S'}#success
        except Exception as e:
            print(e)
            results = {'code': 'F'}#failure
    else:
        results = {'code': 'ND'}#failure
        
  return jsonify(results)

@app.route("/basket", methods=["GET", "POST"])
@login_required
def basket():
    noData = False
    print("Inside Basket")
    print("Logged in user:: ",current_user.first_name)
    basketItems = BasketMaster.query.filter_by(user_name=current_user.user_name).all()
    print("len(basketItems):: ",len(basketItems))
    if(len(basketItems)==0):
        noData = True
    totalPrice = 0;
    totalDiscount = 0;
    for item in basketItems:
    
        discountPrice=discountedPrice(getOGPrice(item.product.product_id),getDiscount(item.product.product_id))
        totalPrice+=discountPrice*item.qty
        discount = (getOGPrice(item.product.product_id) - discountPrice)*item.qty
        totalDiscount+=discount
    
    #return "Welcome "+current_user.first_name


    return render_template("basket.html",noData=noData, current_user=current_user, basketItems=basketItems,discountedPrice = discountedPrice, getOGPrice=getOGPrice, getDiscount=getDiscount, totalPrice=totalPrice, totalDiscount=totalDiscount)

@app.route("/saveBasket", methods=["POST"])
@login_required
def saveBasket():
   
    print("Inside Save Basket")
    print("Logged in user:: ",current_user.first_name)
    if request.method == "POST":
        result = {"code":"S"}
        status = {}
        OFS=[]
        if(current_user.first_name):
            basketData = request.get_json()
            
            for item in basketData:
                item_id = item.get("itemId")
                qty = int(item.get("quantity"))
                try:
                    basketItem = BasketMaster.query.filter_by(user_name=current_user.user_name, item_id=item_id ).first()
                    if basketItem:
                        if(qty>getStockQty(basketItem.product_id)):
                            status[item_id]="O"
                            OFS.append(basketItem.product.product_name+" available qty("+str(getStockQty(basketItem.product_id))+")")
                        else:
                            basketItem.qty = qty
                            db.session.commit()
                            status[item_id]="S"
                except Exception as e:
                    print(e)
                    status[item_id]="F"
            result["status"]=status
            result["OFS"]=OFS
        else:
            result={"code":"F"}
        return jsonify(result)

@app.route("/placeOrder", methods=["POST"])
@login_required
def placeOrder():
   
    print("Inside placeOrder")
    print("Logged in user:: ",current_user.first_name)
    if request.method == "POST":
        result = {"code":"S"}
        status = {}
        OFS=[]
        if(current_user.first_name):
            orderReq = request.get_json()
            basketItems = BasketMaster.query.filter_by(user_name=current_user.user_name).all()
            if(len(basketItems) == 0):
                result = {"code":"ND"}
            else:
                for basketItem in basketItems:
                    if(basketItem.qty>getStockQty(basketItem.product_id)):
                        status[basketItem.item_id]="O"
                        OFS.append(basketItem.product.product_name+" available qty("+str(getStockQty(basketItem.product_id))+")")
                    else:
                        status[basketItem.item_id]="S"
                    
        else:
            result={"code":"F"}
        result["status"]=status
        result["OFS"]=OFS
        return jsonify(result)

@app.route("/orderConfirmation", methods=["GET", "POST"])
@login_required
def orderConfirmation():
    if request.method == "GET":
        noData = False
        print("Inside orderConfirmation")
        print("Logged in user:: ",current_user.first_name)
        basketItems = BasketMaster.query.filter_by(user_name=current_user.user_name).all()
        print("len(basketItems):: ",len(basketItems))
        if(len(basketItems)==0):
            noData = True
        totalPrice = 0;
        totalDiscount = 0;
        for item in basketItems:
        
            discountPrice=discountedPrice(getOGPrice(item.product.product_id),getDiscount(item.product.product_id))
            totalPrice+=discountPrice*item.qty
            discount = (getOGPrice(item.product.product_id) - discountPrice)*item.qty
            totalDiscount+=discount
        
    #return "Welcome "+current_user.first_name


    return render_template("orderConfirmation.html",noData=noData, current_user=current_user, basketItems=basketItems,discountedPrice = discountedPrice, getOGPrice=getOGPrice, getDiscount=getDiscount, totalPrice=totalPrice, totalDiscount=totalDiscount)

@app.route("/placeOrderConfirm", methods=["POST"])
@login_required
def placeOrderConfirm():
   
    print("Inside placeOrderConfirm")
    print("Logged in user:: ",current_user.first_name)
    if request.method == "POST":
        result = {"code":"S"}
        status = {}
        successItems = []
        OFS=[]
        if(current_user.first_name):
            orderReq = request.get_json()
            print("orderReq:: ",orderReq)
            basketData = orderReq['cartData']
            address = orderReq['address']
            contact = orderReq['contact']
            orderId = generate_order_id()#order id for the entire batch
            for cartItem in basketData:
                itemId = cartItem['itemId']
                quantity = int(cartItem['quantity'])
                price = float(cartItem['itemPrice'])
                totalItemPrice = price*quantity
                try:
                    basketItem = BasketMaster.query.filter_by(user_name=current_user.user_name, item_id=itemId ).first()
                    if basketItem:
                        if(quantity>getStockQty(basketItem.product_id)):
                            status[itemId]="O"
                            OFS.append(basketItem.product.product_name+" available qty("+str(getStockQty(basketItem.product_id))+")")
                        else:
                            
                            
                            orderItem = Orders(item_id=itemId, 
                                         user_name = current_user.user_name,
                                         product_id = basketItem.product_id,
                                         qty = basketItem.qty,
                                         order_price = price,
                                        order_id = orderId,
                                        address = address,
                                        contact_no = contact,
                                        total_price = totalItemPrice )
                            db.session.add(orderItem)
                            basketItem.product.product_stock -= quantity
                            db.session.delete(basketItem)
                            db.session.commit()
                            status[itemId]="S"
                            successItems.append(itemId)
                    else:
                        status[itemId]="ND"
                except Exception as e:
                    print(e)
                    status[itemId]="F"
                    db.session.rollback()

                    
        else:
            result={"code":"F"}
        if(len(successItems)==0):
            result={"code":"F"}
        else:
            result['orderId'] = orderId
            result["status"]=status
            result["OFS"]=OFS
        return jsonify(result)

@app.route('/orders', methods=['GET'])
@login_required
def orders():
    print("Inside orders")
    print("Logged in user:: ",current_user.first_name)

    if request.method == "GET":
        query = Orders.query.filter(Orders.user_name==current_user.user_name)
        query = query.order_by(Orders.created_at.desc())  # Sorting by created date (descending)
        myOrders = query.all()
        orderDataAll = {}
        def getItemObj(order):
            item = {}
            item['item_id'] = order.item_id
            item['name'] = order.product.product_name
            item['qty'] = order.qty
            item['price_per_unit'] = order.order_price
            item['total_price'] = order.total_price
            return item
        for order in myOrders:
            
            orderId = order.order_id
            if orderId not in orderDataAll:
                orderData = {}
                orderData['created_at'] = order.created_at
                orderData['address'] = order.address
                orderData['total_qty'] = order.qty
                orderData['total_price'] = order.total_price
                status = order.status
                if(status == "P"):
                    status = "placed"
                elif(status == "D"):
                    status = "delivered"
                orderData['status'] = status
                orderData['itemList'] = []
                orderData['itemList'].append(getItemObj(order))
                orderDataAll[orderId] = orderData
            else:
                #order id previously captured, just append item details
                orderDataAll[orderId]['total_qty'] += order.qty
                orderDataAll[orderId]['total_price'] += order.total_price
                orderDataAll[orderId]['itemList'].append(getItemObj(order))
        noData = False
        if(len(orderDataAll) == 0):
            noData = True
        print("orderData: ",orderDataAll)
        return render_template('orders.html', noData=noData, orderDataAll=orderDataAll)
#Admin routes ###################

@app.route("/admin", methods=["GET","POST"])
def admin_login():
    print("Inside admin Login route")
    form = LoginForm()
    if form.validate_on_submit():
        print("admin form.validate_on_submit()")
        user = User.query.filter_by(user_name=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                print("password matched")
                login_user(user)
                if(user.user_type == "SM"):
                    return redirect(url_for('admin_category'))#admin_category is the default landing page
            print("admin password did not matched")
            flash("Incorrect Details, Please try again.")
        print("admin user does not exists")
    print("admin not form.validate_on_submit()")
    return render_template('admin/admin_login.html', form=form)

@app.route("/admin/home", methods=["GET", "POST"])
@login_required
def admin_home():
    return render_template('admin/admin_home.html', current_user=current_user)

@app.route("/admin/product", methods=["GET","POST"])
@login_required
def admin_product():
    # Products = Product.query.all()
    #query all products in asc order of their name
    Products = Product.query.order_by(Product.product_name.asc()).all()
    noData=True
    if(len(Products)>0):
        noData=False
    return render_template('admin/product_management.html',Products=Products, current_user=current_user, noData=noData)

@app.route("/admin/category", methods=["GET","POST"])
@login_required
def admin_category():
    Categories = Category.query.order_by(Category.category_name.asc()).all()
    noData=True
    if(len(Categories)>0):
        noData=False
    return render_template('admin/category_management.html', Categories=Categories,noData=noData, current_user=current_user)

@app.route('/admin/addProduct', methods=['POST', 'GET'])
@login_required
def addProduct():
  global categories_master #update category master after adding new product
  categories = Category.query.all()
  if request.method == "GET":

      return render_template('admin/addProduct.html', categories=categories)
  if request.method == "POST":
      product_name = str(request.form.get('product-name')).capitalize()
      product_description = request.form.get('product-description')
      product_price = request.form.get('product-price')
      product_quantity = request.form.get('product-quantity')
      product_category = request.form.get('product-category')
      product_type = request.form.get('product-type')
      product_unit = request.form.get('product-unit')
      product_discount = request.form.get('product-discount')
      product_manufactured_date = datetime.strptime(request.form.get('product-manufactured-date'), "%Y-%m-%d").date()
      product_expiry_date = datetime.strptime(request.form.get('product-expiry-date'), "%Y-%m-%d").date()
     
      print("name: ",product_name)
      print("man date: ",product_manufactured_date)
      # Handle the uploaded image file
      product_image = request.files['product-image']

      product = Product.query.filter(func.lower(Product.product_name)==product_name.lower()).first()
      if product:
          flash("product with same name already exists.","error")
      else:
        if product_image:
            # Save the image to a specific directory
            image_filename = secure_filename(product_image.filename)
            unique_filename = generate_unique_filename(image_filename)
            image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], unique_filename)
            product_image.save(image_path)
            #now add product to database
            new_product = Product(product_name=product_name,
                                    product_desc=product_description,
                                    product_img=unique_filename,
                                    product_price_per_unit=product_price,
                                    product_stock=product_quantity,
                                    product_exp_date=product_expiry_date,
                                    product_man_date=product_manufactured_date,
                                    product_discount=product_discount,
                                    veg_nveg=product_type,
                                    category_id=product_category,
                                    product_unit=product_unit
                                    )
            db.session.add(new_product)
            db.session.commit()
            flash("Product added successfully.","success")
            categories_master = Category.query.all()
      return render_template('/admin/addProduct.html', categories=categories)
          #photos.save(request.files.get('product-image'),name=secrets.token_hex(10) + "." )

@app.route('/admin/editProduct/<product_id>', methods=['POST', 'GET'])
@login_required
def editProduct(product_id):
  print("edit product for: product id: ",product_id)
  global categories_master #update category master after adding new product
  categories = Category.query.all()
  if request.method == "GET":
      
      product = Product.query.filter(Product.product_id==product_id).first()
      if product:
          return render_template('admin/editProduct.html', product=product,categories=categories)
    
  if request.method == "POST":
      product_name = str(request.form.get('product-name')).capitalize()
      product_description = request.form.get('product-description')
      product_price = request.form.get('product-price')
      product_quantity = request.form.get('product-quantity')
      product_category = request.form.get('product-category')
      product_type = request.form.get('product-type')
      product_unit = request.form.get('product-unit')
      product_discount = request.form.get('product-discount')
      product_manufactured_date = datetime.strptime(request.form.get('product-manufactured-date'), "%Y-%m-%d").date()
      product_expiry_date = datetime.strptime(request.form.get('product-expiry-date'), "%Y-%m-%d").date()
     
      print("name: ",product_name)
      print("man date: ",product_manufactured_date)
      # Handle the uploaded image file
      product_image = request.files['product-image']

      product = Product.query.filter(func.lower(Product.product_name)==product_name.lower() ,Product.product_id != product_id ).first()
      if product:
          flash("The given product name already exists.","error")
      else:
        product = Product.query.filter_by(product_id=product_id).first()
        if product:
            try:
                product.product_name =  product_name
                product.product_desc = product_description
                product.product_price_per_unit = product_price
                product.product_stock=product_quantity
                product.category_id=product_category
                product.veg_nveg=product_type
                product.product_unit=product_unit
                product.product_discount=product_discount
                product.product_man_date=product_manufactured_date
                product.product_exp_date=product_expiry_date
                if product_image:
                    # Save the image to a specific directory
                    image_filename = secure_filename(product_image.filename)
                    unique_filename = generate_unique_filename(image_filename)
                    image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], unique_filename)
                    product_image.save(image_path)
                    product.product_img=unique_filename
                db.session.commit()
                categories_master = Category.query.all()
                flash("Product changes saved successfully.","success")
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("Something went wrong.","error")
      return redirect(url_for('admin_product'))
      #return render_template('/admin/editProduct.html', categories=categories)

@app.route('/admin/deleteProduct', methods=['POST'])
@login_required
def deleteProduct():
  global categories_master
  print("Inside deleteProduct: ",current_user.user_type)
  if (request.method == "POST" and current_user.user_type == "SM"):
    reqData = request.get_json()
    print("Inside deleteProduct: ",reqData)
    productId = reqData.get("productId")
    product = Product.query.filter_by(product_id=productId).first()
    if product:
        try:
            deleteProductTraces(productId)
            #now delete it from product table
            db.session.delete(product)
            db.session.commit()
            results = {'code': 'S'}#success
            categories_master = Category.query.all()
        except Exception as e:
            print(e)
            db.session.rollback()
            results = {'code': 'F'}#failure
    else:
        results = {'code': 'ND'}#no data
        
  return jsonify(results)


@app.route('/admin/addCategory', methods=['POST', 'GET'])
@login_required
def addCategory():
  global categories_master #update category master after adding new product
  
  if request.method == "GET":

      return render_template('admin/addCategory.html')
  if request.method == "POST":
      category_name = str(request.form.get('category-name')).capitalize()
    
      print("category_name: ",category_name)
      
      category = Category.query.filter(func.lower(Category.category_name)==category_name.lower()).first()
      if category:
          flash("category with same name already exists.","error")
      else:
        new_category = Category(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added successfully.","success")
        categories_master = Category.query.all()
      return render_template('/admin/addCategory.html')
          #photos.save(request.files.get('product-image'),name=secrets.token_hex(10) + "." )


@app.route('/admin/editCategory/<category_id>', methods=['POST', 'GET'])
@login_required
def editCategory(category_id):
  print("edit category for: category_id : ",category_id)
  global categories_master #update category master after adding new product
  
  if request.method == "GET":
      
      category = Category.query.filter(Category.category_id==category_id).first()
      if category:
          return render_template('admin/editCategory.html', category=category)
    
  if request.method == "POST":
      category_name = str(request.form.get('category-name')).capitalize()
      
      print("category-name: ",category_name)

      category = Category.query.filter(func.lower(Category.category_name)==category_name.lower() ,Category.category_id != category_id ).first()
      if category:
          flash("The given category name already exists.","error")
      else:
        category = Category.query.filter_by(category_id=category_id).first()
        if category:
            try:
                category.category_name =  category_name
                db.session.commit()
                categories_master = Category.query.all()
                flash("Category changes saved successfully.","success")
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("Something went wrong.","error")
      return render_template('/admin/addCategory.html')


@app.route('/admin/deleteCategory', methods=['POST'])
@login_required
def deleteCategory():
  global categories_master
  if (request.method == "POST" and current_user.user_type == "SM"):
    reqData = request.get_json()
    print("Inside deleteCategory: ",reqData)
    categoryId = reqData.get("categoryId")
    category = Category.query.filter_by(category_id=categoryId).first()
    if category:
        try:
            #first delete all the products in this category
            products = Product.query.filter_by(category_id=categoryId).all()
            for product in products:
                deleteProductTraces(product.product_id)
                db.session.delete(product)
            #now delete the category
            db.session.delete(category)
            db.session.commit()
            results = {'code': 'S'}#success
            categories_master = Category.query.all()
        except Exception as e:
            print(e)
            db.session.rollback()
            results = {'code': 'F'}#failure
    else:
        results = {'code': 'ND'}#no data
        
  return jsonify(results)
#################################

# Add all restful controllers
from application.api import LoginAPI, RegisterAPI, InventoryAPI, BasketAPI, OrderAPI,SearchAPI, AdminLoginAPI, AdminCategoryAPI, AdminProductAPI, AdminDashboard, AdminProductGenAPI

api.add_resource(LoginAPI, "/api/login")
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(InventoryAPI, "/api/inventory")
api.add_resource(BasketAPI, "/api/basket") 
api.add_resource(OrderAPI, "/api/order")
api.add_resource(SearchAPI, "/api/search")
#admin
api.add_resource(AdminLoginAPI, "/api/admin/login")
api.add_resource(AdminCategoryAPI, "/api/admin/category")
api.add_resource(AdminProductAPI, "/api/admin/product")
api.add_resource(AdminDashboard, "/api/admin/dashboard")
api.add_resource(AdminProductGenAPI, "/api/admin/productReport")

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8080)