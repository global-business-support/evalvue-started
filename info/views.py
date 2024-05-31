from urllib.parse import quote
from django.shortcuts import render,redirect
from django.http import JsonResponse
import pytz
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponseRedirect
from django.urls import reverse
import pyodbc
import json
import random
import requests
import re
import random
from datetime import datetime, timedelta
from django.db import connection,IntegrityError,transaction
from info import aadhar, organization, review
from info.constant import *
from info.utility import convert_to_ist_time, hash_password, populateAddOrganizationData, save_image, send_email, validate_image, validate_organization, verify_password
from .employee import *
from .organization import *
from .response import *
from .review import *
from . aadhar import *
import logging
from .cache import *
import jwt
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger('info')

class CreateUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                name = data.get('name')
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                password = data.get('password')
                logger.info(data)
                res.is_user_register_successfull = True
                if not re.match(r'(?=.{3,25}$)[a-zA-Z]+(?:\s[a-zA-Z]+)?(?:\s[a-zA-Z]+)?$',name):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid Name'
                elif not re.match(r'^\d{10}$', mobile_number):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid mobile number'
                elif not re.match(r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid email'
                elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$', password):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid password'

                if(not res.is_user_register_successfull):
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)

                with connection.cursor() as cursor:
                    cursor.execute("Select count(UserId) from [User] where Email = %s or MobileNumber = %s",[email,mobile_number])
                    count = cursor.fetchone()[0]
                    if count > 0:
                        res.is_user_register_successfull = False
                        res.error = 'User Alreary Exists with this Email and Mobile Number'
                    else:
                        password = hash_password(password, salt)
                        cursor.execute("INSERT INTO [User] (Name, Email, MobileNumber, Password, CreatedOn,IsVerified) VALUES (%s, %s, %s, %s,GETDATE(),%s)",
                                    [name, email, mobile_number, password,0]) 
                        
                    
                    if not res.is_user_register_successfull:
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_user_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_user_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EmployeeAPIView(APIView):
    @csrf_exempt
    def post(emp,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                user_id = data.get('user_id')
                organization_id = data.get('organization_id')
                logger.info(data)
                res.is_employee_mapped_to_organization_successfull = False
                
                with connection.cursor() as cursor:
                    cursor.execute("select EmployeeId from EmployeeOrganizationMapping where OrganizationId = %s ORDER BY CreatedOn DESC",[organization_id])
                    employee_id_results = cursor.fetchall()
                    if employee_id_results:
                        employee_list = []
                        for employee_id_result in employee_id_results:
                            employee_id = employee_id_result[0]
                            cursor.execute("SELECT EmployeeId, Name, Email, MobileNumber, Image, AadharNumber,Designation FROM Employee WHERE EmployeeId = %s", [employee_id])
                            employee_details = cursor.fetchall()
                            for emp_id,emp_name,emp_email,emp_mobile,emp_image,emp_aadhar,emp_designation in employee_details:
                                emp = employee()
                                emp.employee_id = emp_id
                                emp.aadhar_number = emp_aadhar
                                emp.employee_image = emp_image
                                emp.employee_name = emp_name
                                emp.email = emp_email
                                emp.mobile_number = emp_mobile
                                emp.designation = emp_designation
                                employee_list.append(emp.to_dict())
                        res.is_employee_mapped_to_organization_successfull = True                    
                        res.user_id = user_id
                        res.organization_id=organization_id
                        res.employee_list = employee_list
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)
            
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_employee_mapped_to_organization_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_mapped_to_organization_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateEmployeeAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                user_id = data.get('user_id')
                organization_id = data.get('organization_id')
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                employee_image = data.get('employee_image')
                aadhar_number = data.get('aadhar_number')
                confirm_aadhar_number = data.get('confirm_aadhar_number')
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                designation = data.get('designation')
                employee_name = first_name + " " + last_name
                logger.info(data)
                res.is_employee_register_successfull = True
                if not re.match(r'(?=.{3,25}$)[a-zA-Z]+(?:\s[a-zA-Z]+)?(?:\s[a-zA-Z]+)?$',employee_name):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid Name'
                elif not re.match(r"^\d{12}$",aadhar_number):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid aadhar'
                elif aadhar_number != confirm_aadhar_number:
                    res.is_employee_register_successfull = False
                    res.error = 'Aadhar number not matched'
                elif not re.match( r"^(?:(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*)|(?:\".+\"))@(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})(?::\d+)?$",email):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid email'
                elif not re.match(r'^\d{10}$', mobile_number):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid mobile number'
                
                if(not res.is_employee_register_successfull):
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                res.user_id = user_id
                res.organization_id = organization_id
                with connection.cursor() as cursor:
                    cursor.execute("SELECT EmployeeId, Name FROM Employee where AadharNumber = %s",[aadhar_number])
                    employee_details_by_aadhar_number = cursor.fetchone()

                    if employee_details_by_aadhar_number:
                        employee_id_by_aadhar_number = employee_details_by_aadhar_number[0]
                        employee_name_by_aadhar_number = employee_details_by_aadhar_number[1]
                        cursor.execute("SELECT OrganizationId from EmployeeOrganizationMapping where EmployeeId = %s and StatusId = 1 ",[employee_id_by_aadhar_number])
                        organization_id_already_mapped = cursor.fetchone()[0]

                        if organization_id_already_mapped:
                            cursor.execute(" SELECT Name from Organization where OrganizationId = %s",[organization_id_already_mapped])
                            organization_name = cursor.fetchone()[0]

                            if organization_name:
                                res.error = employee_already_mapped_to_organization.format(employee_name_by_aadhar_number,organization_name)
                                res.is_employee_register_successfull = False
                            else:
                                raise Exception(organization_name_not_found.format(organization_id_already_mapped))
                        else:
                            cursor.execute("INSERT into EmployeeOrganizationMapping(EmployeeId,OrganizationId,StatusId,CreatedOn) values(%s,%s,%s,GETDATE())",[employee_id_by_aadhar_number,organization_id,1])
                            res.is_employee_register_successfull = True
                    else:
                        is_image_valid = validate_image(employee_image,res)
                        if is_image_valid:
                            employee_image = save_image(employee_image_path,employee_image)
                        else:
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                        cursor.execute("INSERT INTO Employee (Name, Email, MobileNumber, Image, AadharNumber, Designation, CreatedOn) VALUES (%s, %s, %s, %s, %s,%s, GETDATE())",[employee_name, email, mobile_number, employee_image, aadhar_number, designation])
                        cursor.execute("SELECT EmployeeId FROM Employee where AadharNumber = %s",[aadhar_number])
                        employee_id_for_organization_mapping = cursor.fetchone()[0]
                        cursor.execute("INSERT into EmployeeOrganizationMapping(EmployeeId,OrganizationId,StatusId,CreatedOn) values(%s,%s,%s,GETDATE())",[employee_id_for_organization_mapping,organization_id,1])
                        res.is_employee_register_successfull = True
                        return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_employee_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                email = data.get('email')
                password = data.get('password')
                logger.info(data)
                res.is_login_successfull = True
                res.is_user_verified = True
                if not email or not password:
                    res.is_login_successfull = False
                    res.error = 'Email and password are required'
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT UserId, Password,IsVerified FROM [User] WHERE Email = %s", [email])
                        user_details = cursor.fetchone()
                        if user_details :
                            user_id = user_details[0]
                            stored_password = user_details[1]
                            is_verified = user_details[2]
                            ok = verify_password(stored_password, password, salt)
                            if ok and is_verified == 1:
                                res.user_id = user_id
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
                            elif ok and is_verified == 0:
                                res.is_user_verified = False
                                res.is_login_successfull = False
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
                            else:
                                res.is_login_successfull = False
                                res.error = 'Inavalid credentials'
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            res.is_login_successfull = False
                            res.error = 'Inavalid credentials'
                            return JsonResponse(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST) 

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_login_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_login_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateReviewAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                user_id = data.get('user_id')
                organization_id = data.get('organization_id')
                employee_id = data.get('employee_id')
                comment = data.get('comment')
                image = data.get('image')
                rating = data.get('rating')
                logger.info(data)
                if image:
                    image = save_image(review_image_path,image)
                with connection.cursor() as cursor:
                    cursor.execute("INSERT into Review(Comment, Image, Rating, CreatedOn) values(%s,%s,%s, GETDATE())",[comment,image,rating])
                    cursor.execute("SELECT max(ReviewId) from Review")
                    review_id_inserted_row = cursor.fetchone()

                    if review_id_inserted_row:
                        review_id = review_id_inserted_row[0]
                        cursor.execute("INSERT into ReviewEmployeeOrganizationMapping(ReviewId, OrganizationId, EmployeeId, CreatedOn) values(%s,%s,%s,GETDATE())",[review_id,organization_id,employee_id])

                    res.is_review_added_successfull = True
                    res.user_id = user_id
                    res.organization_id = organization_id
                    res.employee_id = employee_id
                    return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
                
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_review_added_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_added_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ReviewAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                user_id = data.get('user_id')
                organization_id = data.get('organization_id')
                employee_id = data.get('employee_id')
                logger.info(data)
                res.is_review_mapped_to_employee_successfull = True

                with connection.cursor() as cursor:
                    cursor.execute("SELECT EmployeeId, Name, Email, MobileNumber, Image, AadharNumber, Designation, CreatedOn from Employee where EmployeeId = %s",[employee_id])
                    employee_details = cursor.fetchone()
                    employee_list = []
                    emp = employee()
                    emp.employee_id = employee_details[0]
                    emp.employee_name = employee_details[1]
                    emp.email = employee_details[2]
                    emp.mobile_number = employee_details[3]
                    emp.employee_image = employee_details[4]
                    emp.aadhar_number = employee_details[5]
                    emp.designation = employee_details[6]
                    employee_list.append(emp.to_dict())

                    cursor.execute("SELECT ReviewId from ReviewEmployeeOrganizationMapping Where EmployeeId = %s and OrganizationId = %s ORDER BY CreatedOn DESC",[employee_id,organization_id])
                    review_id_results = cursor.fetchall()
                    if review_id_results:
                        review_list = []
                        for review_id_result in review_id_results:
                            review_id = review_id_result[0]
                            cursor.execute("SELECT ReviewId, Comment, Image, Rating, CreatedOn from Review where ReviewId = %s",[review_id])
                            reviews_details = cursor.fetchall()
                            for rev_id, rev_comment, rev_image, rev_rating,rev_created_on in reviews_details:
                                rev = review()
                                rev.review_id = rev_id
                                rev.comment = rev_comment
                                rev.image = rev_image
                                rev.rating = rev_rating
                                rev.created_on = convert_to_ist_time(rev_created_on)
                                review_list.append(rev.to_dict())
                        res.is_review_mapped_to_employee_successfull = True
                        res.review_list = review_list
                        res.employee_id = employee_id
                        res.user_id = user_id
                        res.organization_id = organization_id
                    else:
                        res.is_review_mapped_to_employee_successfull = False
                    res.employee_list = employee_list
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_review_mapped_to_employee_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_mapped_to_employee_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShootOtpAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                email = data.get("email")
                logger.info(data)
                res.otp_send_successfull = False
                if not re.match(r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email):
                    res.otp_send_successfull = False
                    res.error = 'Invalid email'
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT UserId, Email from [User] where email = %s",[email])
                        email_result = cursor.fetchone()
                        if email_result:
                            otp_number = ''.join(random.choices('0123456789', k=6))
                            cursor.execute("INSERT into [OTP] (Email, OtpNumber, Is_Verified, CreatedOn) VALUES(%s,%s,%s,GETDATE())",[email_result[1], otp_number,False])

                            ok = send_email(email_result[1],email_otp_template_path,{'otp_number': otp_number})
                            if ok:
                                res.otp_send_successfull = True
                                res.user_id = email_result[0]
                                res.email = email_result[1]
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.otp_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.otp_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
class VerifyOtpAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                user_id = data.get("user_id")
                email = data.get("email")
                otp_number = data.get("otp_number")
                logger.info(data)
                res.otp_verified_successfull = False
                with connection.cursor() as cursor:
                    cursor.execute("SELECT OtpNumber,CreatedOn from OTP where email = %s and Is_Verified = %s ORDER BY CreatedOn desc",[email,0])
                    otp_result = cursor.fetchone()
                    if otp_result:
                        cursor.execute("SELECT GETDATE()")
                        sql_server_time = cursor.fetchone()[0]
                        created_on = otp_result[1]
                        created_time = datetime.strptime(str(created_on), '%Y-%m-%d %H:%M:%S.%f')  # Convert created_time string to datetime object

                        expiration_time = created_time + timedelta(minutes=2)
                        if sql_server_time > expiration_time:
                            res.otp_is_expired = True
                            res.user_id = user_id
                        elif otp_number != otp_result[0]:
                            res.incorrect_otp = True
                            res.user_id = user_id
                        elif otp_result[0] == otp_number:
                            res.otp_verified_successfull = True
                            cursor.execute("UPDATE [User] SET IsVerified = %s WHERE Email = %s",[1,email])
                            res.is_email_verified_successfull = True
                            res.email = email
                            res.user_id = user_id
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.otp_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.otp_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdatePasswordAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                user_id = data.get("user_id")
                password = data.get("password")
                logger.info(data)
                res.password_updated_successFull = False

                if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$', password):
                    res.password_updated_successFull = False
                    res.error = 'Choose strong password'
                else:
                    password = hash_password(password,salt)
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE [User] SET Password = %s, ModifiedOn = GETDATE() where UserId = %s",[password,user_id])
                        res.password_updated_successFull = True
                return Response(res.convertToJSON(), status = status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.password_updated_successFull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.password_updated_successFull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OrganizationAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        try:
            data = request.data
            user_id = data.get('user_id')
            logger.info(data)
            res = response()
            res.user_id = user_id
            with connection.cursor() as cursor:
                cursor.execute("select OrganizationId, IsVerified from UserOrganizationMapping where UserId = %s ORDER BY CreatedOn DESC",[user_id])
                organization_details_by_user_id = cursor.fetchall()
                if organization_details_by_user_id:
                    res.is_organization_mapped = True
                    organization_id_list = []
                    organization_verified_dict = {}
                    for organization_detail in organization_details_by_user_id:
                        organization_id_list.append(str(organization_detail[0]))
                        organization_verified_dict[organization_detail[0]] = organization_detail[1]
                    strr = ','.join(organization_id_list)
                    cursor.execute("select OrganizationId, Name, Image, SectorId, ListedId, CountryId,StateId,CityId,Area,PinCode from Organization where OrganizationId In ({}) ORDER BY CreatedOn DESC".format(strr))
                    organization_detail_list_by_id = cursor.fetchall()
                    organization_detail_list = []
                    for id,name,image,sector_id,listed_id,country_id,state_id,city_id,area,pincode in organization_detail_list_by_id:
                        org = organization()
                        org.organization_id = id
                        org.name = name
                        org.image = image
                        org.sector_name = sector_type_data[sector_id]['Name']
                        org.listed_name = listed_type_data[listed_id]['Name']
                        org.country_name = country_data[country_id]['Name']
                        org.state_name = state_data[state_id]['Name']
                        org.city_name = city_data[city_id]['Name']
                        org.area = area
                        org.pincode = pincode
                        org.organization_verified = organization_verified_dict[id]
                        organization_detail_list.append(org.to_dict())
                    res.organization_list = organization_detail_list
                    return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
                else: 
                    res.is_organization_mapped = False
                    populateAddOrganizationData(res)
                    return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateOrganizationAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                user_id = data.get("user_id")
                organization_name = data.get("organization_name")
                organization_image = data.get("organization_image")
                document_type_id = data.get("document_type_id")
                document_number = data.get("document_number")
                gstin = data.get("gstin")
                sector_id = data.get("sector_id")
                listed_id = data.get("listed_id")
                country_id = data.get("country_id")
                state_id = data.get("state_id")
                city_id = data.get("city_id")
                area = data.get("area")
                pincode = data.get("pincode")
                number_of_employee = data.get("number_of_employee")
                document_file = data.get("document_file")
                logger.info(data)
                with connection.cursor() as cursor:
                    is_valid = validate_organization(document_number,res)
                    if is_valid:
                        is_image_valid = validate_image(organization_image,res)
                        if is_image_valid:
                            organization_image = save_image(organization_image_path,organization_image)
                        else:
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                        document_file = save_image(document_image_path,document_file)
                        cursor.execute("Insert into Organization(Name,Image,DocumentTypeId,DocumentNumber,GSTIN,SectorId,ListedId,CountryId,StateId,CityId,Area,PinCode,DocumentFile,NumberOfEmployee,CreatedOn) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,GETDATE())",
                                       [organization_name,organization_image,document_type_id,document_number,gstin,sector_id,listed_id,country_id,state_id,city_id,area,pincode,document_file,number_of_employee])
                        cursor.execute("Select OrganizationId from Organization where DocumentNumber = %s",[document_number])
                        organization_details = cursor.fetchone()
                        organization_id = organization_details[0]
                        cursor.execute("Insert into UserOrganizationMapping(UserId, OrganizationId, IsVerified,CreatedOn) values (%s,%s,%s,GETDATE())",[user_id,organization_id,0])
                        res.is_organization_register_successfull = True
                        res.user_id = user_id
                        res.organization_id = organization_id
                        return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
                    else:
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_organization_created_successfully = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_organization_created_successfully = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddOrganizationAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        logger.info(data)
        res = response()
        res.user_id = user_id
        try:
            with transaction.atomic():
                populateAddOrganizationData(res)
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_organization_created_successfully = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_organization_created_successfully = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DashboardFeedAPIview(APIView):
    @csrf_exempt
    def post(self,request):
        try:
            data = request.data
            user_id = data.get('user_id')
            logger.info(data)
            res = response()
            res.user_id = user_id
            with connection.cursor() as cursor:
                cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,org.OrganizationId,org.Name,emp.EmployeeId,emp.Name,emp.Designation,org.Image,emp.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId ORDER BY r.CreatedOn DESC")
                rows = cursor.fetchall()
                reviews = []
                if rows:
                    for row in rows:
                        sql_server_time = row[3]
                        formatted_time = convert_to_ist_time(sql_server_time)
                        rev = review()
                        rev.review_id = row[0]
                        rev.comment = row[1]
                        rev.rating = row[2]
                        rev.created_on = formatted_time
                        rev.organization_id = row[4]
                        rev.organization_name = row[5]
                        rev.employee_id = row[6]
                        rev.employee_name = row[7]
                        rev.designation = row[8]
                        rev.organization_image = row[9]
                        rev.employee_image = row[10]
                        reviews.append(rev.to_dict())
                    res.dashboard_list = reviews
                    res.is_review_mapped = True
                else:
                    res.is_review_mapped = False
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_review_mapped = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_mapped = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchByAadharAPIview(APIView):
    @csrf_exempt
    def post(self,request):
        try:
            data = request.data
            aadhar_number = data.get('aadhar_number')
            logger.info(data)
            res = response()
            aadhar_number = '%'+ aadhar_number + '%'
            with connection.cursor() as cursor:
                cursor.execute("SELECT emp.EmployeeId,emp.Name,emp.Email,emp.MobileNumber,emp.Image,emp.AadharNumber,emp.CreatedOn,emp.Designation,eom.organizationId,org.Name,org.Image FROM EmployeeOrganizationMapping eom JOIN Employee emp ON eom.EmployeeId = emp.EmployeeId JOIN Organization org ON eom.OrganizationId = org.OrganizationId where AadharNumber LIKE %s",[aadhar_number])
                rows = cursor.fetchall()
                print(rows)
                employees = []
                if rows:
                    for row in rows:
                        adh = aadhar()
                        adh.employee_id = row[0]
                        adh.employee_name = row[1]
                        adh.email = row[2]
                        adh.mobile_number = row[3]
                        adh.employee_image = row[4]
                        adh.aadhar_number = row[5]
                        adh.created_on = row[6]
                        adh.designation = row[7]
                        adh.organization_id = row[8]
                        adh.organization_name = row[9]
                        adh.organization_image = row[10]
                        employees.append(adh.to_dict())
                    res.employees_list_by_aadhar = employees
                    res.employees_mapped_to_aadhar = True
                else:
                    res.employees_mapped_to_aadhar = False
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.employees_mapped_to_aadhar = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.employees_mapped_to_aadhar = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
    
                

