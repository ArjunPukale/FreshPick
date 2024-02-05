from application.workers import celery
import logging
from datetime import datetime
from application.models import Orders, User,Product, AdminReportMaster
from flask import current_app as app
from application.database import db
from flask_mail import Mail,Message
from celery.schedules import crontab
import csv
from io import StringIO
import time
import os
from datetime import datetime

# Set up a logger
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('celery_task.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# @celery.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(crontab(hour=16, minute=0), send_mail_no_orders_today.s(), name='no orders today mail')

@celery.task()
def print_hello():
    print("Hello from Celery!")
    logger.info("Hello from Celery!")
    return "Hello from Celery!"

@celery.task()
def print_current_time_job():
    logger.info("START :: print_current_time_job")
    now = datetime.now()
    dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
    logger.info("now in task: %s", dt_string)
    logger.info("END :: print_current_time_job")
    return dt_string


@celery.task()
def just_say_hello(name):
    print("Inside Tasks")
    print("Hello {}".format(name))


@celery.task()
def send_mail_no_orders_today():
# Fetch user's who have not placed any orders today
# First, get the list of users who have placed orders today
    try:
        mail = Mail(app)
        today = datetime.now().date()  # Get the current date
        orders_today = Orders.query.filter(Orders.created_at >= today).all()
        print("orders_today::length::", len(orders_today))
        logger.info("orders_today::length::"+str(len(orders_today)))
        # Now, let's get the list of all users
        all_users = User.query.all()

        # Find the users who haven't placed any orders today
        users_without_orders_today = [user.user_name for user in all_users if user.user_name not in [order.user_name for order in orders_today]]
        users_without_orders_today.append('arjunpukale@gmail.com')
        print("users_without_orders_today::", users_without_orders_today)
        logger.info("users_without_orders_today::"+ str(users_without_orders_today))
        subject='No Orders Today'
        body = "Freshpick is missing you :("
        for user in users_without_orders_today:
            try:
                recipients = [user]
                message = Message(subject=subject, recipients=recipients, body=body, sender='arjunpukale@gmail.com')
                mail.send(message)
                break #temporary
            except Exception as e:
                print("Exception in sending mail to:",user)
                logger.info("Exception in sending mail to:"+str(user))
        
                print(e)
    except Exception as e:
        print(e)

@celery.task()
def generate_product_report( report_id):
#generate product report for admin
    try:
        logger.info("Product Report Generation started ################")
        print("Product Report Generation started ################")
        logger.info("Product Report Generation report_id: "+str(report_id))
        print("report_id::",report_id)
        # Query the database to get product details
        products = Product.query.all()

        # Prepare data for CSV
        field_names = ['product_id', 'product_name', 'product_desc', 'product_stock']  # Add all required fields
        data = StringIO()
        csv_writer = csv.DictWriter(data, fieldnames=field_names)
        csv_writer.writeheader()

        for product in products:
            csv_writer.writerow({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_desc': product.product_desc,
                'product_stock': product.product_stock,
                # Add other fields accordingly
            })

        # Save the CSV to a file or cloud storage (example: save to local filesystem)
        current_dir = os.path.abspath(os.path.dirname(__file__))
        reportFolderPath=os.path.join(current_dir, '../admin_reports')
        filename = "product_report.csv"
        report_path = os.path.join(reportFolderPath, filename)
            
        with open(report_path, 'w') as file:
            file.write(data.getvalue())
        
        logger.info("Product Report Generation product_report.csv file generated")
        # Simulate a delay for testing (10 seconds)
        time.sleep(10)
        logger.info("Product Report Generation simulation delay over")
        # Update the AdminReportMaster record with the generated report details
        report = AdminReportMaster.query.filter_by(report_id=report_id).first()
        if report:
            report.filename = filename
            report.status = 'Y'
            db.session.commit()
            logger.info("Product Report Generation AdminReportMaster updated")
            print("Product Report Generation AdminReportMaster updated")
        else:
            logger.info("Product Report Generation AdminReportMaster entry not found")
            print("Product Report Generation AdminReportMaster entry not found")
    except Exception as e:
        logger.info("Product Report Generation Exception occurred::"+str(e))
        print(e)
        report = AdminReportMaster.query.filter_by(report_id=report_id).first()
        if report:
            report.status = 'E'
            db.session.commit()
        print(f"Error generating report: {str(e)}")

@celery.task
def send_order_report():
    # Get the first and last day of the current month
    now = datetime.now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    mail = Mail(app)
    # Query all users
    users = User.query.all()

    for user in users:
        # Query orders for the current user in the current month
        orders = Orders.query.filter(
            Orders.user_name == user.user_name,
            Orders.created_at >= first_day
        ).all()

        # If the user has orders in the current month, send the order report
        if orders:
            # Create a TSV string with order data
            tsv_data = "item_id\tuser_name\tproduct_id\tqty\torder_price\torder_id\tcreated_at\ttotal_price\tstatus\taddress\tcontact_no\n"
            for order in orders:
                # Use tab ('\t') as the field separator
                tsv_data += f"{order.item_id}\t{order.user_name}\t{order.product_id}\t{order.qty}\t{order.order_price}\t{order.order_id}\t{order.created_at}\t{order.total_price}\t{order.status}\t{order.address}\t{order.contact_no}\n"

            # Now you can use tsv_data as needed.

            # Send the TSV as an attachment in an email to the current user
            subject = 'Your Order Report for the Current Month'
            body = f"Dear {user.first_name},\n\nPlease find attached your order report for the current month.\n\nBest regards,\nYour App Team"

            try:
                recipients = [user.user_name, "arjunpukale@gmail.com"]
                message = Message(subject=subject, recipients=recipients, body=body, sender='arjunpukale@gmail.com')
                message.attach("order_report.tsv", "text/tab-separated-values", tsv_data)
                mail.send(message)
                break  # temporary
            except Exception as e:
                print("Exception in sending mail to:", user.user_name)
                logger.info("Exception in sending mail to:" + str(user.user_name))
                print(e)
