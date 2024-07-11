from datetime import datetime
from grpc import Status
import requests
from rest_framework.response import Response
from evalvue import settings
import os
from info import constant, payment, response
from .cache import *
from .payment import *
from .response import *
from django.db import connection,IntegrityError,transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import hashlib
import uuid
import logging
import pytz
from info.constant import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status



logger = logging.getLogger('info')

def save_image(folder_name,image):
    project_root = settings.BASE_DIR
    

    # Construct the full path for the folder
    folder_path = os.path.join(project_root, folder_name)
    folder_db_path = os.path.join(constant.database_root,folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the full path for the file
    unique_id = uuid.uuid4()
    file_path = os.path.join(folder_path,str(unique_id) + image.name)
    file_db_path = folder_db_path + "/" + str(unique_id) + image.name

    with open(file_path, 'wb') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return file_db_path

def send_email(to_email,template_name,place_holder):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                msg =  render_to_string(template_name,place_holder)
                
                if to_email:
                    email = EmailMessage(
                        subject = "OTP Verification",
                        body = msg,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to = [to_email],
                        
                    )
                    email.content_subtype = 'html'                        
                    email.send(fail_silently=False)
                    return True
    except IntegrityError as e:
        logger.exception('Database integrity error: {}'.format(str(e)))
        return False
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False

def hash_password(password, salt):
    password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return password_hash

def verify_password(stored_password, provided_password, salt):
    password_hash = hashlib.sha256((provided_password + salt).encode('utf-8')).hexdigest()
    return password_hash == stored_password

def validate_organization(document_number,res):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("Select OrganizationId, Name from Organization where DocumentNumber = %s",[document_number])
                result = cursor.fetchone()
                if result:
                    res.is_organization_register_successfull = False
                    res.error = constant.organization_found_document_number.format(document_number)
                    return False
                else:
                    return True
    except IntegrityError as e:
        logger.exception('Database integrity error: {}'.format(str(e)))
        return False
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False
    
ALLOWED_EXTENSIONS = {'.png', '.jpeg', '.jpg'}
def validate_file_extension(image,res):
    try:
        file_extension = os.path.splitext(image.name)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            res.is_image_validate = True
            res.error = constant.file_validation_extension_error
            return False
        else:
            return True
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False

def validate_file_size(image,res):
    try:
        file_size = 1024 * 1024 * 2  #2MB file
        if image.size > file_size:
            res.is_file_validate = True
            res.error = constant.file_validation_size_error
            return False
        else:
            return True
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False
def delete_file(file_path):
    try:
        # Check if the file exists
        if os.path.isfile(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        return False    


def populateAddOrganizationData(res):
    res.document_type = document_type_data
    res.sector_type = sector_type_data
    res.listed_type = listed_type_data
    res.country = country_data
    res.state = state_data
    res.city = city_data

def convert_to_ist_time(sql_server_time):
    formatted_time = sql_server_time.strftime("%d %B at %I:%M %p")
    return formatted_time

def extract_path(url):
    # Split the URL by '/' and join the necessary parts
    parts = url.split('/')
    extracted_path = '/'.join(parts[4:])
    return extracted_path

def validate_employee(email,mobile_number,aadhar_number,res):
    if not mobile_number and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EmployeeId, Name FROM Employee where Email = %s",[email])
            employee_details_by_email = cursor.fetchone()
            if employee_details_by_email:
                employee_id_by_email = employee_details_by_email[0] 
                cursor.execute("SELECT OrganizationId from EmployeeOrganizationMapping where EmployeeId = %s and StatusId = 1 ",[employee_id_by_email])
                organization_id_already_mapped = cursor.fetchone()
                if organization_id_already_mapped:
                    res.is_employee_register_successfull = False
                    res.error = constant.employee_already_mapped_to_organization_by_email.format(email)
                    return True
    if not email and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EmployeeId, Name FROM Employee where MobileNumber = %s",[mobile_number])
            employee_details_by_mobile_number = cursor.fetchone()
            if employee_details_by_mobile_number:
                employee_id_by_mobile_number = employee_details_by_mobile_number[0] 
                cursor.execute("SELECT OrganizationId from EmployeeOrganizationMapping where EmployeeId = %s and StatusId = 1 ",[employee_id_by_mobile_number])
                organization_id_already_mapped = cursor.fetchone()
                if organization_id_already_mapped:
                    res.is_employee_register_successfull = False
                    res.error = constant.employee_already_mapped_to_organization_by_mobile_number.format(mobile_number)
                    return True
    if not email and not mobile_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT EmployeeId, Name FROM Employee where AadharNumber = %s",[aadhar_number])
            employee_details_by_aadhar_number = cursor.fetchone()
            if employee_details_by_aadhar_number:
                employee_id_by_aadhar_number = employee_details_by_aadhar_number[0]
                cursor.execute("SELECT OrganizationId from EmployeeOrganizationMapping where EmployeeId = %s and StatusId = 1 ",[employee_id_by_aadhar_number])
                organization_id_already_mapped = cursor.fetchone()
                if organization_id_already_mapped:
                    res.is_employee_register_successfull = False
                    res.error = constant.employee_already_mapped_to_organization_by_aadhar.format(aadhar_number)
                    return True
    
def validate_employee_on_edit(employee_id,email,mobile_number,aadhar_number,res):
    if not mobile_number and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Email from Employee WHERE EmployeeId != %s and Email = %s",[employee_id,email])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.email_already_exist_error
                return True
    if not email and not aadhar_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MobileNumber from Employee WHERE EmployeeId != %s and MobileNumber = %s",[employee_id,mobile_number])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.mobile_number_already_exist_error
                return True
    if not email and not mobile_number:
        with connection.cursor() as cursor:
            cursor.execute("SELECT AadharNumber from Employee WHERE EmployeeId != %s and AadharNumber = %s",[employee_id,aadhar_number])
            result = cursor.fetchone()
            if result:
                res.employee_edit_sucessfull = False
                res.error = constant.aadhar_number_already_exist_error
                return True
    
class CustomObject:
    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email

def generate_reciept(subscription_id,res,pay):
    try:
        url = settings.payment_url + 'razorpay/payment/receipt/'
        params = {
            'subscription_id' : subscription_id,
        }
        response_data = requests.post(url, params=params)
        generate_reciept_data = []
        if response_data.status_code == 200:
            data = response_data.json()
            pay.organization_name = data.get('organization_name')
            pay.amount = data.get('amount')
            pay.razorpay_order_id = data.get('razorpay_order_id')
            pay.payment_status = data.get('payment_status')
            pay.transaction_id = data.get('transaction_id')
            pay.payment_mode = data.get('payment_mode')
            pay.date = data.get('date_time')
            pay.upi = data.get('payment_through_upi')
            generate_reciept_data.append(pay.to_dict())
            res.generate_reciept_data = generate_reciept_data
            res.is_generate_reciept_data_send_successfull = True
        else:
            res.error = receipt_error_message_1
            res.is_generate_reciept_data_send_successfull = False
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.exception('An unexpected error occurred: {}'.format(str(e)))
        res.is_generate_reciept_data_send_successfull = False
        res.error = generic_error_message