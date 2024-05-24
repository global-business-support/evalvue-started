from evalvue import settings
import os
from info import constant
from .cache import *

def save_image(folder_name,image):
    project_root = settings.BASE_DIR
    

    # Construct the full path for the folder
    folder_path = os.path.join(project_root, folder_name)
    folder_db_path = os.path.join(constant.database_root,folder_name)

    print(folder_path)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Construct the full path for the file
    file_path = os.path.join(folder_path, image.name)
    file_db_path = folder_db_path + "/" + image.name

    print(file_path,file_db_path)

    with open(file_path, 'wb') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return file_db_path



from django.db import connection,IntegrityError,transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def send_email(to_email,template_name,place_holder):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # cursor.execute("INSERT into [OTP] (Email, OtpNumber, Is_Verified, CreatedOn) VALUES(%s,%s,%s,GETDATE())",[to_email, otp_number,False])
                msg =  render_to_string(template_name,place_holder)
                
                if to_email:
                    email = EmailMessage(
                        subject = "OTP Verification",
                        body = msg,
                        from_email='jaydeepkarode5656@gmail.com',
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


import hashlib

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


    # with connection.cursor() as cursor:
    #     cursor.execute("select DocumentTypeId, Name from DocumentType")
    #     document_type_result = cursor.fetchall()
        
    #     if document_type_result:
    #         document_type = {}

    #         for doc_id, doc_name in document_type_result:
    #             document_type[doc_id] = doc_name
    #         res.document_type = document_type
    #     else:
    #         raise Exception(document_type_data_not_found)
        
    #     cursor.execute("select SectorTypeId, Name from SectorType")
    #     sector_type_result = cursor.fetchall()
    #     if sector_type_result:
    #         sector_type = {}
    #         for sector_id, sector_name in sector_type_result:
    #             sector_type[sector_id] = sector_name
    #         res.sector_type = sector_type
    #     else:
    #         raise Exception(sector_type_data_not_found)
        
    #     cursor.execute("select ListedTypeId, Name from ListedType")
    #     listed_type_result = cursor.fetchall()
    #     if listed_type_result:
    #         listed_type = {}
    #         for listed_id, listed_name in listed_type_result:
    #             listed_type[listed_id] = listed_name
    #         res.listed_type = listed_type
    #     else:
    #         raise Exception(listed_type_data_not_found)
        
    #     cursor.execute("select CountryId, Name from County")
    #     country_result = cursor.fetchall()
    #     if country_result:
    #         country = {}
    #         for country_id, country_name in country_result:
    #             country[country_id] = country_name
    #         res.country = country
    #     else:
    #         raise Exception(country_data_not_found)
        
    #     cursor.execute("select StateId, Name from State")
    #     state_result = cursor.fetchall()
    #     if state_result:
    #         state = {}
    #         for state_id, state_name in state_result:
    #             state[state_id] = state_name
    #         res.state = state
    #     else:
    #         raise Exception(state_data_not_found)
        
    #     cursor.execute("select cityId, Name from City")
    #     city_result = cursor.fetchall()
    #     if city_result:
    #         city = {}
    #         for city_id, city_name in city_result:
    #             city[city_id] = city_name
    #         res.city = city
    #     else:
    #         raise Exception(city_data_not_found)
        


