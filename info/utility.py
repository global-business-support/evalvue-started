from evalvue import settings
import os
from info import constant
from .cache import *
from django.db import connection,IntegrityError,transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import hashlib


def save_image(folder_name,image):
    project_root = settings.BASE_DIR
    

    # Construct the full path for the folder
    folder_path = os.path.join(project_root, folder_name)
    folder_db_path = os.path.join(constant.database_root,folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the full path for the file
    file_path = os.path.join(folder_path, image.name)
    file_db_path = folder_db_path + "/" + image.name

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
        print('Database integrity error: {}'.format(str(e)))
        return False
    except Exception as e:
        print('Database integrity error: {}'.format(str(e)))
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
                    res.error = constant.organization_found_document_number.format(result[1],document_number)
                    return False
                else:
                    return True
    except IntegrityError as e:
        print('Database integrity error: {}'.format(str(e)))
        return False
    except Exception as e:
        print('Database integrity error: {}'.format(str(e)))
        return False

def populateAddOrganizationData(res):
    res.document_type = document_type_data
    res.sector_type = sector_type_data
    res.listed_type = listed_type_data
    res.country = country_data
    res.state = state_data
    res.city = city_data
