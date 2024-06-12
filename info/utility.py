from evalvue import settings
import os
from info import constant
from .cache import *
from django.db import connection,IntegrityError,transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import hashlib
import uuid
import logging
import pytz

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
        file_size = 1024 * 1024 * 2
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
    ist_timezone = pytz.timezone('Asia/Kolkata')
    sql_server_time_utc = sql_server_time.replace(tzinfo=pytz.utc)
    ist_time = sql_server_time_utc.astimezone(ist_timezone)
    formatted_time = ist_time.strftime("%d %B at %I:%M %p")
    return formatted_time

def extract_path(url):
    # Split the URL by '/' and join the necessary parts
    parts = url.split('/')
    extracted_path = '/'.join(parts[4:])
    return extracted_path

def validate_employee(employee_id,email,mobile_number,aadhar_number,res):
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


