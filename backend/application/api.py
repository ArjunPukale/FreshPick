from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError
from application.models import User, BasketMaster, Product, Orders, Category, AdminReportMaster
from application.database import db
from flask import current_app as app
import werkzeug
from flask import abort
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import jsonify, request
#for jwt token
from flask_jwt_extended import jwt_required, create_access_token, current_user, get_jwt_identity
import logging
import os
import datetime
from datetime import datetime, timedelta
import random
from decimal import Decimal
from sqlalchemy import func
from werkzeug.utils import secure_filename
import uuid
from .masterdata import MasterData
from .tasks import generate_product_report
import base64
from flask_caching import Cache
bcrypt = Bcrypt(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# Business Errors:
# BE1001 - username is required
# BE1002 - password is required
# BE1003 - Invalid email
# BE1004 - Incorrect username/password
# BE1005 - Invalid access



def configure_logger(name, log_file):
    # Create the full path to the log file
    log_file_path = os.path.join('Logs', log_file)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler and set the log level
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

##### Helper Functions ###########
def getUserBasket(username):
    outerMap={}
    try:
        basketItems = BasketMaster.query.filter_by(user_name=username).all()
        print("len(basketItems):: ",len(basketItems))
        if(len(basketItems)==0):
            outerMap['code']="ND"
            outerMap['basket']={}
        else:
            basketData = {} #key=product_id, value=qty
            for item in basketItems:
                basketData[item.product_id]=item.qty
            outerMap['basket'] = basketData
            outerMap['code']="S"
    except Exception as e:
        print(e)
        outerMap['code']="F"
        outerMap['basket']={}
    return outerMap


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

def discountedPrice(ogPrice, discount):
    print(ogPrice, type(ogPrice), discount, type(discount))
    return ogPrice*(Decimal(1) - discount*Decimal(0.01))

# @cache.cached(timeout=5)#5sec
def getOGPrice(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        ogPrice =  product.product_price_per_unit
        #discount = product.product_discount
        return ogPrice
    else:
        return None
    
# @cache.cached(timeout=5)#5sec
def getDiscount(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        #ogPrice =  product.product_price_per_unit
        discount = product.product_discount
        return discount #0-100
    else:
        return None
    
def generate_unique_filename(filename):
    _, ext = os.path.splitext(filename)
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename

def deleteProductTraces(productId):
    #first delete basket items of this product
    basketItems = BasketMaster.query.filter_by(product_id=productId).all()
    for basketItem in basketItems:
        db.session.delete(basketItem)

    #delete order entries of this product
    orderItems = Orders.query.filter_by(product_id=productId).all()
    for orderItem in orderItems:
        db.session.delete(orderItem)

    db.session.commit()
    return None

def generate_report_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_id = f"report_{timestamp}"
    return report_id

#Login API -------------------------------------------------
login_user_parser = reqparse.RequestParser()
login_user_parser.add_argument('username')
login_user_parser.add_argument('password')
class LoginAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Login', 'Login.log')     
    def post(self):
        args = login_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        
        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="password is required")

        if "@" in username:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")
        logprefix = "| " +username+" | "
        user = User.query.filter_by(user_name=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                print("password matched")
                self.logger.info(logprefix+'password matched')
                login_user(user)
                #get user's vasket data
                basketOutMap = getUserBasket(username)
                basketData = {}
                if(basketOutMap['code'] == "S"):
                    basketData = basketOutMap['basket']
                
                outerMap = {"username":user.user_name,
                            "firstName":user.first_name,
                            "lastName": user.last_name,
                            "phoneNumber":user.phone_number,
                            "address":user.address,
                            "token":create_access_token(identity=user.user_name),
                            "basket": basketData}
                self.logger.info(logprefix+'outerMap:: '+str(outerMap))
                return jsonify(outerMap)
            else:
                print("password not matched")
                self.logger.info(logprefix+'password not matched')
                raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            

        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    
    @jwt_required()
    def get(self):
        print("jwt id: ",get_jwt_identity())
        return jsonify({"msg":"protected data"})
#Login API Ends-------------------------------------------------  


#Register API -------------------------------------------------
register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument('username')
register_user_parser.add_argument('password')
register_user_parser.add_argument('firstName')
register_user_parser.add_argument('lastName')
register_user_parser.add_argument('phoneNumber')
register_user_parser.add_argument('address')

class RegisterAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Register', 'Register.log')  
    def post(self):
        args = register_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        firstName = args.get("firstName", None)
        lastName = args.get("lastName", None)
        phoneNumber = args.get("phoneNumber", None)
        address = args.get("address", None)
        #basic input checks
        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="password is required")

        if "@" in username:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")
        ##############################
        logprefix = "| " +username+" | "
        user = User.query.filter_by(user_name=username).first()
        if user:
            self.logger.info(logprefix+'User already exists !')
            #raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="Username already exists.")
            outerMap = {
                    "code":"F",
                    "msg":"Username already exists.",
                }
        else:
            try:
                hashed_password = bcrypt.generate_password_hash(password)
                new_user = User(user_name=username, password=hashed_password,
                    first_name = str(firstName).upper(),
                    last_name = str(lastName).upper(),
                    phone_number = phoneNumber,
                    address = address)
                db.session.add(new_user)
                db.session.commit()
                self.logger.info(logprefix+'User Registered Successfully !')
                outerMap = {
                    "code":"S",
                    "msg":"Registration successful.",
                }
                
            except Exception as e:
                db.session.rollback()
                self.logger.info(logprefix+'Exception occurred: '+str(e))
                outerMap = {
                    "code":"F",
                    "msg":"some error occured.",
                }
        return jsonify(outerMap)
#Register API ends-------------------------------------------------

#Basket API -------------------------------------------------------
get_user_basket_parser = reqparse.RequestParser()
get_user_basket_parser.add_argument('username')
class BasketAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Basket', 'Basket.log')  
    @jwt_required()   
    def get(self):
        print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        logprefix = "| " +username+" | "
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            try:
                outerMap = getUserBasket(username)
            except Exception as e:
                self.logger.info(logprefix+"Exception:: "+str(e))
                outerMap['code']="F"
                outerMap['basket']={}
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
    @jwt_required()
    def post(self):
        #to add an item in basket
        basketData = request.get_json()
        username = basketData.get("username")
        itemData = basketData.get("item")
        productId = int(itemData.get("productId"))
        qty = int(itemData.get("qty"))
        logprefix = "| " +username+" | "
        self.logger.info(logprefix+"basketData:: "+str(basketData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            #check if the product already exists in user's basket
            basketItem = BasketMaster.query.filter_by(user_name=username, product_id=productId).first()
            if(basketItem):
                outerMap['code']= 'D'#duplicate
            else:
                availQty = getStockQty(productId)
                self.logger.info(logprefix+"availQty:: "+str(availQty))
                if(availQty<qty): #out of stock
                    outerMap['code']='O'
                    outerMap['availQTY']=availQty
                
                else:
                    try:
                        basketItem = BasketMaster(user_name=username, product_id=productId,qty=qty )
                        db.session.add(basketItem)
                        db.session.commit()
                        outerMap['code']='S'

                    except Exception as e:
                        db.session.rollback()
                        self.logger.info(logprefix+"Exception:: "+str(e))
                        outerMap['code']='F'#failure
            #get user's vasket data
            basketOutMap = getUserBasket(username)
            basketData = {}
            if(basketOutMap['code'] == "S"):
                basketData = basketOutMap['basket']
            outerMap['basket']=basketData
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
    
    @jwt_required()   
    def delete(self):
        print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        productId = request.args.get('id')
        logprefix = "delete | " +username+" | productId|"+productId
        productId = int(productId)
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            #check if the product already exists in user's basket
            basketItem = BasketMaster.query.filter_by(user_name=username, product_id=productId).first()
            if(basketItem):
                try:
                    db.session.delete(basketItem)
                    db.session.commit()
                    outerMap['code']= 'S';#success
                except Exception as e:
                    print(e)
                    outerMap['code']= 'F';#failure
            else:
                outerMap['code']= 'ND';#product not found
            #get user's vasket data
            basketOutMap = getUserBasket(username)
            basketData = {}
            if(basketOutMap['code'] == "S"):
                basketData = basketOutMap['basket']
            outerMap['basket']=basketData
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
                
    @jwt_required()
    def put(self):
        # To save the user's basket
        print("Inside Save Basket")
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "put | " +username+" |"
        self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            status = {}
            OOS={}
            basketData = requestData.get("basket")
            for productId in basketData:
                qty = int(basketData[productId])
                try:
                    basketItem = BasketMaster.query.filter_by(user_name=username, product_id=int(productId) ).first()
                    if basketItem:
                        if(qty>getStockQty(basketItem.product_id)):
                            status[productId]="O"
                            OOS[productId]=getStockQty(productId)
                        else:
                            basketItem.qty = qty
                            db.session.commit()
                            status[productId]="S"
                except Exception as e:
                    print(e)
                    status[productId]="F"
            outerMap["status"]=status
            outerMap["OOS"]=OOS
            #get user's vasket data
            basketOutMap = getUserBasket(username)
            basketData = {}
            if(basketOutMap['code'] == "S"):
                basketData = basketOutMap['basket']
            outerMap['basket']=basketData
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap) 
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
                           
#Inventory API -------------------------------------------------

class InventoryAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Inventory', 'Inventory.log') 
    @jwt_required()
    def get(self):
        print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        if(username == get_jwt_identity()):
            return jsonify({"categories":MasterData.CATEGORY_MASTER,
                            "products":MasterData.PRODUCT_MASTER})
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
    
#Inventory API ends-------------------------------------------------

#Order API -------------------------------------------------------

class OrderAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Orders', 'Orders.log')

    @jwt_required()   
    def get(self):
        print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        logprefix = "| " +username+" | "
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {'code':'S'}
            try:
                query = Orders.query.filter(Orders.user_name==username)
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
                self.logger.info(logprefix+"myOrders::size:: "+str(len(myOrders)))
                for order in myOrders:
                    orderId = order.order_id
                    if orderId not in orderDataAll:
                        orderData = {}
                        orderData['order_id'] = orderId
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
            except Exception as e:
                print(e)
                self.logger.info(logprefix+"Exception:: "+str(e))
                outerMap['code']='F'
            noData = False
            if(len(orderDataAll) == 0):
                noData = True
                outerMap['code']='ND'
                outerMap['orders']=[]
            else:
                sorted_orders = sorted(orderDataAll.values(), key=lambda x: x['created_at'], reverse=True)
                outerMap['orders']=sorted_orders
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
             
    @jwt_required()   
    def post(self):
        # To place an order
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "OrderAPI post | " +username+" |"
        self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {"code":"S"}
            status = {}
            successItems = []
            OOS={}
            basketData = requestData['basket']
            address = requestData['address']
            contact = requestData['contact']
            orderId = generate_order_id()#order id for the entire batch
            for productId in basketData:
                quantity = int(basketData[productId])
                discounted_price=discountedPrice(getOGPrice(productId),getDiscount(productId))
                totalItemPrice = discounted_price*quantity
                try:
                    basketItem = BasketMaster.query.filter_by(user_name=username, product_id=int(productId) ).first()
                    if basketItem:
                        if(quantity>getStockQty(basketItem.product_id)):
                            # OUT OF STOCK !!!
                            self.logger.info(logprefix+"basketItem.product_id:: "+str(basketItem.product_id)+" out of stock !")
                            status[productId]="O"
                            OOS[productId]=getStockQty(productId)
                            outerMap['code']='PS' # partial success
                        else:
                            orderItem = Orders(item_id=basketItem.item_id, 
                                         user_name = username,
                                         product_id = basketItem.product_id,
                                         qty = basketItem.qty,
                                         order_price = basketItem.product.product_price_per_unit,
                                        order_id = orderId,
                                        address = address,
                                        contact_no = contact,
                                        total_price = totalItemPrice )
                            db.session.add(orderItem)
                            basketItem.product.product_stock -= quantity
                            db.session.delete(basketItem)
                            db.session.commit()
                            status[productId]="S"
                            successItems.append(productId)
                    else:
                        status[productId]="ND"
                except Exception as e:
                    print(e)
                    status[productId]="F"
                    db.session.rollback()
                    self.logger.info(logprefix+"Exception:: "+str(e))
            if(len(successItems)==0):
                outerMap['code']='F'
            outerMap['orderId'] = orderId
            outerMap["status"]=status
            outerMap["OOS"]=OOS
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
                 
# Order API ends ##########################

#Search API -------------------------------------------------------

class SearchAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Search', 'Search.log')
    @jwt_required()   
    def post(self):
        # To search for a product
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "SearchAPI post | " +username+" |"
        self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            outerMap['productList']=[]
            search_query = requestData.get('query')
            categoryId = requestData.get('categoryId')
            min_discount = requestData.get('minDiscountValue')
            veg_nonveg = requestData.get('vegNonveg')
            min_price = requestData.get('minPrice')
            max_price = requestData.get('maxPrice')

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
            self.logger.info(logprefix+"products::size "+str(len(products)))
            if(len(products)==0):
                outerMap['code']='ND'
            else:
                for product in products:
                    productId = product.product_id
                    outerMap['productList'].append(str(productId))
                outerMap['code']='S'
            self.logger.info(logprefix+"outerMap:: "+str(outerMap))
            return jsonify(outerMap)
        else:
            self.logger.info(logprefix+"Invalid access:: get_jwt_identity():"+get_jwt_identity())
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
                   
############ ADMIN APIS #####################

#Admin Login API -------------------------------------------------
login_user_parser = reqparse.RequestParser()
login_user_parser.add_argument('username')
login_user_parser.add_argument('password')
class AdminLoginAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('AdminLogin', 'Admin_Login.log')     
    def post(self):
        args = login_user_parser.parse_args()
        username = args.get("username", None)
        password = args.get("password", None)
        
        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="password is required")

        if "@" in username:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")
        logprefix = "| " +username+" | "
        user = User.query.filter_by(user_name=username).first()
        if user:
            if(bcrypt.check_password_hash(user.password, password) and user.user_type == "SM"):
                print("password matched")
                self.logger.info(logprefix+'password matched')
                login_user(user)
                
                outerMap = {"username":user.user_name,
                            "firstName":user.first_name,
                            "lastName": user.last_name,
                            "phoneNumber":user.phone_number,
                            "address":user.address,
                            "token":create_access_token(identity=user.user_name),
                            }
                self.logger.info(logprefix+'outerMap:: '+str(outerMap))
                return jsonify(outerMap)
            else:
                print("password not matched")
                self.logger.info(logprefix+'password not matched')
                raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            

        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    
    @jwt_required()
    def get(self):
        print("jwt id: ",get_jwt_identity())
        return jsonify({"msg":"protected data"})
#Admin Login API Ends-------------------------------------------------  

# Admin Category API ##############
class AdminCategoryAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Admin_Category', 'Admin_Category.log')
    @jwt_required()   
    def post(self):
        # To add a new category
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "Admin:: Category:: post | " +username+" |"
        self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            outerMap['categories']={}
            outerMap['products']={}
            try:
                category_name = requestData.get("categoryName").capitalize()
                category = Category.query.filter(func.lower(Category.category_name)==category_name.lower()).first()
                if category:
                    outerMap['code']='D' #duplicate name 
                else:
                    new_category = Category(category_name=category_name)
                    db.session.add(new_category)
                    db.session.commit()
                    outerMap['code']='S'
                    #update category,product master data
                    MasterData.loadCategoryData()
                    outerMap['categories']=MasterData.CATEGORY_MASTER
                    outerMap['products']=MasterData.PRODUCT_MASTER
            except Exception as e:
                outerMap['code']='F'
                db.session.rollback()
                self.logger.info(logprefix+"Exception:: "+str(e))
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    @jwt_required()   
    def put(self):
        # To edit a category
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "Admin:: Category:: edit | " +username+" |"
        self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            outerMap['categories']={}
            outerMap['products']={}
            category_id = requestData.get("categoryId")
            category_name = str(requestData.get("categoryName")).capitalize()
      
            print("category-name for edit:: ",category_name, category_id)

            category = Category.query.filter(func.lower(Category.category_name)==category_name.lower() ,Category.category_id != category_id ).first()
            if category:
                outerMap['code']='D'
            else:
                category = Category.query.filter_by(category_id=category_id).first()
                if category:
                    try:
                        category.category_name =  category_name
                        db.session.commit()
                        outerMap['code']='S'
                        #update category,product master data
                        MasterData.loadCategoryData()
                        outerMap['categories']=MasterData.CATEGORY_MASTER
                        outerMap['products']=MasterData.PRODUCT_MASTER
                    except Exception as e:
                        print(e)
                        outerMap['code']='F'
                        db.session.rollback()
                        self.logger.info(logprefix+"Exception:: "+str(e))
            self.logger.info(logprefix+'outerMap:: '+str(outerMap))
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    @jwt_required()   
    def delete(self):
        #delete a category
        username = request.args.get('username')
        productId = request.args.get('id')
        logprefix = "Admin:: Category:: delete | " +username+" |"
        categoryId = int(productId)
        self.logger.info(logprefix+'categoryId:: '+str(categoryId))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
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
                    #update category,product master data
                    MasterData.loadCategoryData()
                    outerMap['categories']=MasterData.CATEGORY_MASTER
                    outerMap['products']=MasterData.PRODUCT_MASTER
                    outerMap['code']='S'
                except Exception as e:
                    print(e)
                    db.session.rollback()
                    outerMap['code']='F'
                    self.logger.info(logprefix+"Exception:: "+str(e))
            else:
                self.logger.info(logprefix+"No such category found!!! ")
                outerMap['code']='ND'
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
  

   
# Admin Category API ENDS ##############

# Admin Product API ##############
class AdminProductAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('Admin_Product', 'Admin_Product.log')
    @jwt_required()   
    def post(self):
        # To add a new product
        username = str(request.form.get('username'))
        logprefix = "Admin:: Product:: post | " +username+" |"
        
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            outerMap['categories']={}
            outerMap['products']={}
 
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
            self.logger.info(logprefix+"request.form.items():: "+str(request.form.items()))
            print("name: ",product_name)
            print("man date: ",product_manufactured_date)
            # Handle the uploaded image file
            product_image = request.files['product-image']
            product = Product.query.filter(func.lower(Product.product_name)==product_name.lower()).first()
            if product:
                outerMap['code']='D' #duplicate product
            if product_image:
                # Save the image to a specific directory
                try:
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
                    #update category,product master data
                    MasterData.loadCategoryData()
                    outerMap['categories']=MasterData.CATEGORY_MASTER
                    outerMap['products']=MasterData.PRODUCT_MASTER
                    outerMap['code']='S'
                except Exception as e:
                    outerMap['code']='F'
                    db.session.rollback()
                    self.logger.info(logprefix+"Exception:: "+str(e))
                    print(e)
            else:
                outerMap['code']='F'
                self.logger.info(logprefix+"No Image Uploaded !!!")
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    @jwt_required()   
    def put(self):
        # To edit a product
        username = str(request.form.get('username'))
        product_id = request.form.get('productId')
        logprefix = "Admin:: Product:: edit | " +username+" |"
       # self.logger.info(logprefix+"requestData:: "+str(requestData))
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            outerMap['categories']={}
            outerMap['products']={}

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
            product_image = None
            if 'product-image' in request.files:
                product_image = request.files['product-image']
            print("product_image::",product_image)
            product = Product.query.filter(func.lower(Product.product_name)==product_name.lower() ,Product.product_id != product_id ).first()
            if product:
                outerMap['code']='D'
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
                        #update category,product master data
                        MasterData.loadCategoryData()
                        outerMap['categories']=MasterData.CATEGORY_MASTER
                        outerMap['products']=MasterData.PRODUCT_MASTER
                        outerMap['code']='S'
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        outerMap['code']='F'
                        self.logger.info(logprefix+"Exception:: "+str(e))
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    
    @jwt_required()   
    def delete(self):
        #delete a product
        username = request.args.get('username')
        productId = request.args.get('id')
        logprefix = "Admin:: Product:: delete | " +username+" |"
        productId = int(productId)
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            product = Product.query.filter_by(product_id=productId).first()
            if product:
                try:
                    deleteProductTraces(productId)
                    #now delete it from product table
                    db.session.delete(product)
                    db.session.commit()
                    print("Product deleted and committed successfully")
                    #update category,product master data
                    MasterData.loadCategoryData()
                    outerMap['categories']=MasterData.CATEGORY_MASTER
                    outerMap['products']=MasterData.PRODUCT_MASTER
                    outerMap['code']='S'

                except Exception as e:
                    print(e)
                    db.session.rollback()
                    outerMap['code']='F'
                    self.logger.info(logprefix+"Exception:: "+str(e))
            else:
                outerMap['code']='ND'
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    
# Admin Product API ENDS ##############

# Admin dashboard api ###############
class AdminDashboard(Resource):
    def __init__(self):
        self.logger = configure_logger('AdminDashboard', 'AdminDashboard.log') 
    @jwt_required()
    def get(self):
        #print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        if(username == get_jwt_identity()):
            #number of orders today
            today = datetime.now().date()  # Get the current date
            noOfOrdersToday = 0
            try:
                orders_today = Orders.query.filter(Orders.created_at >= today).all()
                noOfOrdersToday = len(orders_today)
            except Exception as e:
                print(e)
                noOfOrdersToday = 0
            return jsonify({"noOfOrdersToday":noOfOrdersToday})
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
   
# Admin dashboard api ends ###############

# Admin Product Report API ##############
class AdminProductGenAPI(Resource):
    def __init__(self):
        self.logger = configure_logger('AdminProductGenAPI', 'AdminProductGenAPI.log')
    @jwt_required()   
    def post(self):
        # To add a new product
        requestData = request.get_json()
        username = requestData.get("username")
        logprefix = "Admin:: Product Gen:: post | " +username+" |"
        
        if(username == get_jwt_identity()):
            #valid user
            outerMap = {}
            try:
                report_id = generate_report_id()
                new_report = AdminReportMaster(
                    report_id=report_id,  # Placeholder ID
                    filename='pending.csv',
                    report_type='Product',
                    status='N'
                )
                db.session.add(new_report)
                db.session.commit()
                task = generate_product_report.apply_async(args=[report_id])
                task_id = task.id
                outerMap['code']='S'
                outerMap['task_id'] = task_id
                outerMap['report_id'] = report_id
            except Exception as e:
                outerMap['code']='F'
                print("Error while generating report")
                self.logger.info(logprefix+"Exception:: "+str(e))

            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1004", error_message="Incorrect username/password")            
    @jwt_required()
    def get(self):
        
        #print("jwt id: ",get_jwt_identity())
        username = request.args.get('username')
        report_id = request.args.get('reportId')
        report_status="N"
        logprefix = "Admin:: ProductReport:: get status | " +username+" |"
        if(username == get_jwt_identity()):
            outerMap={}
            
            try:
                report = AdminReportMaster.query.filter_by(report_id=report_id).first()
                if report:
                    report_status = report.status
                    outerMap['code']='S'
                    outerMap['filename']=report.filename
                    self.logger.info(logprefix+"report status:: "+str(report_status))
                    if(report_status == 'Y'):
                        current_dir = os.path.abspath(os.path.dirname(__file__))
                        reportFolderPath=os.path.join(current_dir, '../admin_reports')
                        filename = report.filename
                        report_path = os.path.join(reportFolderPath, filename)
                        #code to send the csv file in outermap
                        with open(report_path, 'rb') as file:
                            csv_bytes = file.read()
                        # Encode the CSV file bytes to base64
                        csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
                        outerMap['csv_data'] = csv_base64
                    
                else:
                    outerMap['code']='ND'
                    self.logger.info(logprefix+report_id+"::entry not found !!!")
            except Exception as e:
                outerMap['code']='F'
                self.logger.info(logprefix+report_id+"::Exception::"+str(e))
                print(e)
            outerMap['status']=report_status
            return jsonify(outerMap)
        else:
            raise BusinessValidationError(status_code=401, error_code="BE1005", error_message="Invalid access")            
 