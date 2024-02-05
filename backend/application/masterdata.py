from .models import Category, Product
from decimal import Decimal


# HELPER FUNCIONS ###################################
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
        discount = product.product_discount #0-100
        return discount#discountedPrice(ogPrice,discount)
    else:
        return None
def getStockQty(productId):
    product = Product.query.filter_by(product_id=productId).first()

    if product:
        stock =  product.product_stock
        
        return stock
    else:
        return None
######################################################################
class MasterData:
    PRODUCT_MASTER = {}
    CATEGORY_MASTER ={}
    @classmethod
    def loadCategoryData(cls):
        cls.PRODUCT_MASTER = {}
        cls.CATEGORY_MASTER ={}
        categories_master = Category.query.all()
        print("# categories: ",len(categories_master))
        for category in categories_master:
            print(category.category_name,"#products: ",len(category.products))
            cls.CATEGORY_MASTER[category.category_id] = {"name":category.category_name, "products":[]}
            for product in category.products:
                cls.CATEGORY_MASTER[category.category_id]["products"].append(str(product.product_id))
                if(product.product_id not in cls.PRODUCT_MASTER):
                    cls.PRODUCT_MASTER[product.product_id]={}
                    cls.PRODUCT_MASTER[product.product_id]["name"]=product.product_name
                    cls.PRODUCT_MASTER[product.product_id]["product_desc"]=product.product_desc
                    cls.PRODUCT_MASTER[product.product_id]["product_img"]=product.product_img
                    cls.PRODUCT_MASTER[product.product_id]["product_exp_date"]=product.product_exp_date
                    cls.PRODUCT_MASTER[product.product_id]["product_man_date"]=product.product_man_date
                    cls.PRODUCT_MASTER[product.product_id]["veg_nveg"]=product.veg_nveg
                    cls.PRODUCT_MASTER[product.product_id]["category_id"]=str(product.category_id)
                    cls.PRODUCT_MASTER[product.product_id]["product_stock"]=getStockQty(product.product_id)
                    cls.PRODUCT_MASTER[product.product_id]["product_price_per_unit"]=getOGPrice(product.product_id)
                    cls.PRODUCT_MASTER[product.product_id]["product_discount"]=getDiscount(product.product_id)
                    cls.PRODUCT_MASTER[product.product_id]["product_unit"]=product.product_unit
        print("CATEGORY_MASTER:: ",cls.CATEGORY_MASTER)
        print("PRODUCT_MASTER:: ",cls.PRODUCT_MASTER)