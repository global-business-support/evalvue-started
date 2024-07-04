from urllib.parse import quote
from django.shortcuts import render,redirect
from django.http import JsonResponse
import os 
import jwt
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
from evalvue import settings
from info import aadhar, organization, payment, review
from info import constant
from info.common_regex import validate_aadhar_number, validate_comment, validate_designation, validate_document_number, validate_email, validate_gstin, validate_mobile_number, validate_name, validate_organization_name, validate_otp, validate_password, validate_pin_code, validate_referral_code
from info.constant import *
from info.utility import convert_to_ist_time, hash_password, populateAddOrganizationData, save_image, send_email, validate_employee, validate_employee_on_edit, validate_organization, verify_password, extract_path, delete_file
from info.utility import convert_to_ist_time, hash_password, populateAddOrganizationData, save_image, send_email, validate_organization, verify_password, extract_path, delete_file
from info.utility import CustomObject, convert_to_ist_time, hash_password, populateAddOrganizationData, save_image, send_email, validate_file_extension, validate_file_size, validate_organization, verify_password
from .employee import *
from .organization import *
from .response import *
from .review import *
from . aadhar import *
from .payment import *
import logging
from .cache import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger('info')

def capitalize_words(s):
    return s.upper()
    

class CreateUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data
                name = capitalize_words(data.get('name'))
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                password = data.get('password')
                logger.info(data)
                res.is_user_register_successfull = True
                if not validate_name(name):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid Name'
                elif not validate_mobile_number(mobile_number):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid mobile number'
                elif not  validate_email(email):
                    res.is_user_register_successfull = False
                    res.error = 'Invalid email'
                elif not validate_password(password):
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
                user_id = getattr(request, 'user_id', None)
                data = request.data
                organization_id = data.get('organization_id')
                logger.info(data)
                res.is_employee_mapped_to_organization_successfull = False
                
                with connection.cursor() as cursor:
                    cursor.execute("select EmployeeId from EmployeeOrganizationMapping where OrganizationId = %s and StatusId = %s ORDER BY CreatedOn DESC",[organization_id,1])
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
                user_id = getattr(request, 'user_id', None)
                data = request.data
                organization_id = data.get('organization_id')
                first_name = capitalize_words(data.get('first_name'))
                last_name = capitalize_words(data.get('last_name'))
                employee_image = data.get('employee_image')
                aadhar_number = data.get('aadhar_number')
                confirm_aadhar_number = data.get('confirm_aadhar_number')
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                designation = capitalize_words(data.get('designation'))
                employee_name = first_name.strip() + " " + last_name.strip()
                logger.info(data)
                res.is_employee_register_successfull = True
                if not validate_name(employee_name):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid Name'
                elif not validate_aadhar_number(aadhar_number):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid aadhar'
                elif aadhar_number != confirm_aadhar_number:
                    res.is_employee_register_successfull = False
                    res.error = 'Aadhar number not matched'
                elif not validate_email(email):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid email'
                elif not validate_mobile_number(mobile_number):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid mobile number'
                elif not validate_designation(designation):
                    res.is_employee_register_successfull = False
                    res.error = 'Invalid designation'
                
                if not res.is_employee_register_successfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                res.user_id = user_id
                res.organization_id = organization_id
                with connection.cursor() as cursor:
                    if validate_employee(email,None,None,res) or validate_employee(None,mobile_number,None,res) or validate_employee(None,None,aadhar_number,res):
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    else:
                        is_image_valid = validate_file_extension(employee_image,res)
                        is_image_size_valid = validate_file_size(employee_image,res)
                        if is_image_valid and is_image_size_valid:
                            employee_image = save_image(employee_image_path,employee_image)
                        else:
                            res.is_employee_register_successfull = False
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
                res.is_login_successfull = False
                res.is_user_verified = False
                if not email or not password:
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
                                user_data = CustomObject(user_id,email)

                                refresh = RefreshToken.for_user(user_data)
                                access_token = refresh.access_token
                                # token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                                res.refresh  = str(refresh)
                                res.access = str(access_token)
                                res.user_id = user_id
                                res.is_user_verified = True
                                res.is_login_successfull = True
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
                            elif ok and is_verified == 0:
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
                            else:
                                res.error = 'Inavalid credentials'
                                return JsonResponse(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST) 
                        else:
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

    # permission_classes = [IsAuthenticated]
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                user_id = getattr(request, 'user_id', None)
                data = request.data 
                organization_id = data.get('organization_id')
                employee_id = data.get('employee_id')
                comment = data.get('comment')
                image = data.get('image')
                rating = data.get('rating')
                logger.info(data)
                # print(user_idd)
                res.is_review_added_successfull = True
                if not validate_comment(comment):
                    res.is_review_added_successfull = False
                    res.error = 'Invalid comment'
                if not res.is_review_added_successfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                if image is not None:
                    is_image_valid = validate_file_extension(image,res)
                    is_image_size_valid = validate_file_size(image,res)
                    if is_image_valid and is_image_size_valid:
                        review_image = save_image(review_image_path,image)
                    else:
                        res.is_review_added_successfull = False
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                else:
                    review_image = None
                with connection.cursor() as cursor:
                    cursor.execute("INSERT into Review(Comment, Image, Rating, CreatedOn) values(%s,%s,%s, GETDATE())",[comment,review_image,rating])
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
                user_id = getattr(request, 'user_id', None)
                data = request.data 
                organization_id = data.get('organization_id')
                employee_id = data.get('employee_id')
                search_by_aa = data.get('search_by_aa')
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
                    if search_by_aa:
                        cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,org.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId where rem.EmployeeId = %s",[employee_id])
                        rows = cursor.fetchall()
                    else:
                        cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,org.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId where rem.EmployeeId = %s and rem.OrganizationId = %s",[employee_id,organization_id])
                        rows = cursor.fetchall()
                    
                    if rows:
                        review_list = []
                        for row in rows:
                            sql_server_time = row[3]
                            formatted_time = convert_to_ist_time(sql_server_time)
                            rev = review()
                            rev.review_id = row[0]
                            rev.comment = row[1]
                            rev.rating = row[2]
                            rev.created_on = formatted_time
                            rev.image = row[4]
                            rev.organization_id = row[5]
                            rev.organization_name = row[6]
                            rev.organization_image = row[7]
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
                user_verification = data.get("user_verification")
                employee_verification = data.get("employee_verification")
                logger.info(data)
                res.otp_send_successfull = False
                if not validate_email(email):
                    res.otp_send_successfull = False
                    res.error = 'Invalid email'
                else:
                    with connection.cursor() as cursor:
                        if employee_verification:
                            cursor.execute("SELECT EmployeeId, Email from [Employee] where email = %s",[email])
                            email_result = cursor.fetchone()
                        elif user_verification:
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
                        else:
                            res.error = reset_password_email_not_found 
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
                user_verification = data.get("user_verification")
                employee_verification = data.get("employee_verification")
                employee_id = data.get("employee_id")
                organization_id = data.get("organization_id")
                logger.info(data)
                res.otp_verified_successfull = False
                if not validate_otp(otp_number):
                    res.otp_verified_successfull = False
                    res.error = 'Incorrect otp'
                elif not validate_email(email):
                    res.otp_verified_successfull = False
                    res.error = 'Invalid email'   
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
                            if user_verification:
                                cursor.execute("UPDATE [User] SET IsVerified = %s WHERE Email = %s",[1,email])
                                res.is_user_verified_successfull = True
                            elif employee_verification:
                                cursor.execute("INSERT INTO EmployeeOrganizationMapping(EmployeeId,OrganizationId,StatusId,CreatedOn) values(%s,%s,%s,GETDATE())",[employee_id,organization_id,1])
                                res.is_terminated_employee_added_successfull = True
                            res.otp_verified_successfull = True
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

                if not validate_password(password):
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
            user_id = getattr(request, 'user_id', None)
            data = request.data
            logger.info(data)
            res = response()
            res.user_id = user_id
            with connection.cursor() as cursor:
                cursor.execute("select OrganizationId, IsVerified,IsPaid,IsRejected from UserOrganizationMapping where UserId = %s ORDER BY CreatedOn DESC",[user_id])
                organization_details_by_user_id = cursor.fetchall()
                if organization_details_by_user_id:
                    res.is_organization_mapped = True
                    cursor.execute("SELECT COUNT(*) FROM [UserOrganizationMapping] WHERE UserId = %s AND IsPaid = 1;",[user_id])
                    organizations_paid_count = cursor.fetchone()[0]
                    organization_id_list = []
                    organization_verified_dict = {}
                    organization_paid_dict = {}
                    organization_rejected_dict = {}
                    for organization_detail in organization_details_by_user_id:
                        organization_id_list.append(str(organization_detail[0]))
                        organization_verified_dict[organization_detail[0]] = organization_detail[1]
                        organization_paid_dict[organization_detail[0]] = organization_detail[2]
                        organization_rejected_dict[organization_detail[0]] = organization_detail[3]
                    strr = ','.join(organization_id_list)
                    cursor.execute("select OrganizationId, Name, Image, SectorId, ListedId, DocumentNumber,CountryId,StateId,CityId,Area,PinCode from Organization where OrganizationId In ({}) ORDER BY CreatedOn DESC".format(strr))
                    organization_detail_list_by_id = cursor.fetchall()
                    organization_detail_list = []
                    for id,name,image,sector_id,listed_id,document_number,country_id,state_id,city_id,area,pincode in organization_detail_list_by_id:
                        org = organization()
                        org.organization_id = id
                        org.name = name
                        org.image = image
                        org.sector_name = sector_type_data[sector_id]['Name']
                        org.listed_name = listed_type_data[listed_id]['Name']
                        org.country_name = country_data[country_id]['Name']
                        org.state_name = state_data[state_id]['Name']
                        org.city_name = city_data[city_id]['Name']
                        org.document_number = document_number
                        org.area = area
                        org.pincode = pincode
                        org.organization_verified = organization_verified_dict[id]
                        org.organization_paid = organization_paid_dict[id]
                        org.organization_rejected = organization_rejected_dict[id]
                        organization_detail_list.append(org.to_dict())
                    res.organization_list = organization_detail_list
                    res.organizations_paid_count = organizations_paid_count
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
                user_id = getattr(request, 'user_id', None)
                data = request.data
                organization_name = capitalize_words(data.get("organization_name"))
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
                referral_code = data.get("referral_code")
                logger.info(data)
                res.is_organization_register_successfull = True
                if not validate_organization_name(organization_name):
                    res.is_organization_register_successfull = False
                    res.error = 'Invalid organization name'
                elif not validate_document_number(document_number):
                    res.is_organization_register_successfull = False
                    res.error = 'Invalid document number'
                elif not validate_gstin(str(gstin)):
                    res.is_organization_register_successfull = False
                    res.error = 'Invalid GSTIN number'
                elif not validate_pin_code(pincode):
                    res.is_organization_register_successfull = False
                    res.error = 'Invalid pincode'
                elif not validate_referral_code(referral_code):
                    res.is_organization_register_successfull = False
                    res.error = 'Invalid referral code'

                if not res.is_organization_register_successfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                
                with connection.cursor() as cursor:
                    is_valid = validate_organization(document_number,res)
                    if is_valid:
                        is_image_valid = validate_file_extension(organization_image,res)
                        is_image_size_valid = validate_file_size(organization_image,res)

                        if is_image_valid and is_image_size_valid:
                            organization_image = save_image(organization_image_path,organization_image)
                        else:
                            res.is_organization_register_successfull = False
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                        
                        if validate_file_size(document_file,res):
                            document_file = save_image(document_image_path,document_file)
                        else:
                            res.is_organization_register_successfull = False
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                        cursor.execute("Insert into Organization(Name,Image,DocumentTypeId,DocumentNumber,GSTIN,SectorId,ListedId,CountryId,StateId,CityId,Area,PinCode,DocumentFile,NumberOfEmployee,CreatedOn) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,GETDATE())",
                                    [organization_name,organization_image,document_type_id,document_number,gstin,sector_id,listed_id,country_id,state_id,city_id,area,pincode,document_file,number_of_employee])
                        cursor.execute("Select OrganizationId,Name from Organization where DocumentNumber = %s",[document_number])
                        organization_details = cursor.fetchone()
                        organization_id = organization_details[0]
                        organization_name = organization_details[1]
                        cursor.execute("Insert into UserOrganizationMapping(UserId, OrganizationId, IsVerified,CreatedOn,IsPaid,IsRejected) values (%s,%s,%s,GETDATE(),%s,%s)",[user_id,organization_id,0,0,0])
                        if referral_code in referral_codes_data:
                            cursor.execute("INSERT INTO ReferralOrganizationMapping(Code,Name,OrganizationId,OrganizationName,CreatedOn) VALUES(%s,%s,%s,%s,GETDATE())",[referral_code,referral_codes_data[referral_code],organization_id,organization_name])

                        res.is_organization_register_successfull = True
                        res.user_id = user_id
                        res.organization_id = organization_id

                        return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
                    else:
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_organization_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_organization_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddOrganizationAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        user_id = getattr(request, 'user_id', None)
        data = request.data
        logger.info(data)
        res = response()
        res.user_id = user_id
        try:
            with transaction.atomic():
                populateAddOrganizationData(res)
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_organization_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_organization_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DashboardFeedAPIview(APIView):
    @csrf_exempt
    def post(self,request):
        try:
            user_id = getattr(request, 'user_id', None)
            data = request.data
            logger.info(data)
            res = response()
            res.user_id = user_id
            with connection.cursor() as cursor:
                cursor.execute("SELECT rem.ReviewId,r.Comment,r.Rating,r.CreatedOn,r.Image,org.OrganizationId,org.Name,emp.EmployeeId,emp.Name,emp.Designation,org.Image,emp.Image FROM ReviewEmployeeOrganizationMapping rem JOIN Review r ON rem.ReviewId = r.ReviewId JOIN Organization org ON rem.OrganizationId = org.OrganizationId JOIN Employee emp ON rem.EmployeeId = emp.EmployeeId ORDER BY r.CreatedOn DESC")
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
                        rev.image = row[4]
                        rev.organization_id = row[5]
                        rev.organization_name = row[6]
                        rev.employee_id = row[7]
                        rev.employee_name = row[8]
                        rev.designation = row[9]
                        rev.organization_image = row[10]
                        rev.employee_image = row[11]
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
                cursor.execute("SELECT emp.EmployeeId,emp.Name,emp.Email,emp.MobileNumber,emp.Image,emp.AadharNumber,emp.CreatedOn,emp.Designation,eom.OrganizationId,eom.StatusId,org.Name,org.Image FROM EmployeeOrganizationMapping eom JOIN Employee emp ON eom.EmployeeId = emp.EmployeeId JOIN Organization org ON eom.OrganizationId = org.OrganizationId where AadharNumber LIKE %s AND eom.EmployeeOrganizationMappingId = (SELECT TOP 1 eom_inner.EmployeeOrganizationMappingId FROM EmployeeOrganizationMapping eom_inner WHERE eom_inner.EmployeeId = emp.EmployeeId ORDER BY eom_inner.EmployeeOrganizationMappingId DESC)",[aadhar_number])
                rows = cursor.fetchall()
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
                        adh.created_on = convert_to_ist_time(row[6])
                        adh.designation = row[7]
                        adh.organization_id = row[8]
                        adh.status_id = row[9]
                        adh.organization_name = row[10]
                        adh.organization_image = row[11]
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

class TopFiveEmployeeAPIview(APIView):
    def post(self,request):
        user_id = getattr(request, 'user_id', None)
        data = request.data
        logger.info(data)
        res = response()
        try:
            with connection.cursor() as cursor:
                cursor.execute("WITH AverageRatings AS (SELECT Emp.EmployeeId,AVG(Rate.Rating) AS AverageRating FROM [testdb].[dbo].[ReviewEmployeeOrganizationMapping] AS Emp JOIN [testdb].[dbo].[Review] AS Rate ON Emp.ReviewId = Rate.ReviewId GROUP BY Emp.EmployeeId)SELECT TOP 5 AR.EmployeeId,E.Name,E.Designation,E.Image,AR.AverageRating FROM AverageRatings AS AR JOIN [testdb].[dbo].[Employee] AS E ON AR.EmployeeId = E.EmployeeId ORDER BY AR.AverageRating DESC")
                rows = cursor.fetchall()
                top = []
                if rows:
                    for row in rows:
                        top_employee = employee()
                        top_employee.employee_id = row[0]
                        top_employee.employee_name = row[1]
                        top_employee.designation = row[2]
                        top_employee.employee_image = row[3]
                        top_employee.average_rating = row[4]
                        top.append(top_employee.to_dict())
                    res.top_employee = top
                    res.is_top_employee = True
                else:
                    res.is_top_employee = False
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)
    
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EditOrganizationAPIview(APIView):
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                user_id = getattr(request, 'user_id', None)
                data = request.data
                organization_id = data.get("organization_id")
                organization_name = capitalize_words(data.get("organization_name"))
                organization_image = data.get("organization_image")
                sector_id = data.get("sector_id")
                listed_id = data.get("listed_id")
                country_id = data.get("country_id")
                state_id = data.get("state_id")
                city_id = data.get("city_id")
                area = data.get("area")
                pincode = data.get("pincode")
                number_of_employee = data.get("number_of_employee")
                logger.info(data)
                res.organization_edit_sucessfull = True 
                if not validate_organization_name(organization_name):
                    res.organization_edit_sucessfull = False
                    res.error = 'Invalid organization name'
                elif not validate_pin_code(pincode):
                    res.organization_edit_sucessfull = False
                    res.error = 'Invalid pincode'
                if not res.organization_edit_sucessfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT Image FROM Organization WHERE OrganizationId = %s", [organization_id])
                    result = cursor.fetchone()
                    old_image = result[0]
                    if not isinstance(organization_image, str):
                        is_image_valid = validate_file_extension(organization_image,res)
                        is_image_size_valid = validate_file_size(organization_image,res)
                        if is_image_valid and is_image_size_valid:
                            organization_image = save_image(organization_image_path,organization_image)
                            if old_image:
                                image_path = extract_path(old_image)
                                delete_file(image_path)
                        else:
                            res.organization_edit_sucessfull = False
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                        cursor.execute("update [Organization] set Name = %s, Image = %s, SectorId = %s, ListedId = %s,CountryId = %s, StateId = %s, CityId = %s, Area = %s, PinCode = %s,NumberOfEmployee = %s, modifiedOn = GETDATE() WHERE OrganizationId = %s",[organization_name,organization_image,sector_id,listed_id,country_id,state_id,city_id,area,pincode,number_of_employee,organization_id])
                        res.user_id = user_id
                        res.organization_id = organization_id
                        res.organization_edit_sucessfull = True
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
                    else:
                        cursor.execute("update [Organization] set Name = %s, Image = %s, SectorId = %s, ListedId = %s,CountryId = %s, StateId = %s, CityId = %s, Area = %s, PinCode = %s,NumberOfEmployee = %s, modifiedOn = GETDATE() WHERE OrganizationId = %s",[organization_name,organization_image,sector_id,listed_id,country_id,state_id,city_id,area,pincode,number_of_employee,organization_id])
                        res.user_id = user_id
                        res.organization_id = organization_id
                        res.organization_edit_sucessfull = True
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.organization_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.organization_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

              
class EditEmployeeAPIview(APIView):
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                user_id = getattr(request, 'user_id', None)
                data = request.data
                employee_id = data.get("employee_id")
                first_name = capitalize_words(data.get('first_name'))
                last_name = capitalize_words(data.get('last_name'))
                email = data.get("email")
                mobile_number = data.get("mobile_number")   
                designation = capitalize_words(data.get("designation"))
                employee_image = data.get("employee_image")
                logger.info(data)
                employee_name = first_name.strip() + " " + last_name.strip()
                res.employee_edit_sucessfull = True
                if not validate_name(employee_name):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid Name'
                elif not validate_email(email):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid email'
                elif not validate_mobile_number(mobile_number):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid mobile number'
                elif not validate_designation(designation):
                    res.employee_edit_sucessfull = False
                    res.error = 'Invalid designation'
                if not res.employee_edit_sucessfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                if validate_employee_on_edit(employee_id,email,None,None,res) or validate_employee_on_edit(employee_id,None,mobile_number,None,res):
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                with connection.cursor() as cursor:      
                    cursor.execute("SELECT Image FROM employee WHERE EmployeeId = %s", [employee_id])
                    img = cursor.fetchone()
                    old_image = img[0]
                    if not isinstance(employee_image, str):
                        is_image_valid = validate_file_extension(employee_image,res)
                        is_image_size_valid = validate_file_size(employee_image,res)
                        if is_image_valid and is_image_size_valid:
                            employee_image = save_image(employee_image_path,employee_image)
                            if old_image:
                                file_path = extract_path(old_image)
                                delete_file(file_path)
                        else:
                            res.employee_edit_sucessfull = False
                            return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    
                        cursor.execute("update [Employee] set Name = %s, Email = %s, MobileNumber = %s, Designation = %s,Image = %s, modifiedOn = GETDATE() WHERE EmployeeId = %s",[employee_name,email,mobile_number,designation,employee_image,employee_id])
                        res.employee_edit_sucessfull = True
                        res.user_id = user_id
                        res.employee_id = employee_id
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
                    else:
                        cursor.execute("update [Employee] set Name = %s, Email = %s, MobileNumber = %s, Designation = %s, modifiedOn = GETDATE() WHERE EmployeeId = %s",[employee_name,email,mobile_number,designation,employee_id])
                        res.employee_edit_sucessfull = True
                        res.user_id = user_id
                        res.employee_id = employee_id
                        return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)

                
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.employee_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.employee_edit_sucessfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeEditableDataAPIView(APIView):
    @csrf_exempt
    def post(emp,request):
        res = response()
        try:
            with transaction.atomic():
                user_id = getattr(request, 'user_id', None)
                data = request.data
                employee_id = data.get('employee_id')
                logger.info(data)                
                with connection.cursor() as cursor:
                    employee_list = []
                    cursor.execute("SELECT Name, Email, MobileNumber, Image, AadharNumber,Designation FROM Employee WHERE EmployeeId = %s", [employee_id])
                    employee_details = cursor.fetchall()
                    name = employee_details[0][0]
                    parts = name.split()
                    if len(parts) >= 3:
                        first_name = parts[0] + ' ' + parts[1]
                        last_name = parts[2]
                    else:
                        first_name = parts[0]
                        last_name = parts[1]
                    for emp_name,emp_email,emp_mobile,emp_image,emp_aadhar,emp_designation in employee_details:
                        emp = employee()
                        emp.aadhar_number = emp_aadhar
                        emp.employee_image = emp_image
                        emp.first_name = first_name
                        emp.last_name = last_name
                        emp.email = emp_email
                        emp.mobile_number = emp_mobile
                        emp.designation = emp_designation
                        employee_list.append(emp.to_dict())
                res.user_id = user_id
                res.employee_id = employee_id
                res.employee_list = employee_list
                res.employee_editable_data_send_successfull = True
            return Response(res.convertToJSON(), status=status.HTTP_200_OK)
            
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.employee_editable_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.employee_editable_data_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
class OrganizationEditableDataAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        try:
            user_id = getattr(request, 'user_id', None)
            data = request.data
            organization_id = data.get('organization_id')
            rejected_user_reapply = data.get('rejected_user_reapply')
            logger.info(data)
            res = response()
            with connection.cursor() as cursor:
                message_result = False
                if rejected_user_reapply:
                    cursor.execute("Select Top 1 Message,CreatedOn from RejectMessage where UserId = %s and organizationId = %s Order By CreatedOn Desc",[user_id,organization_id])
                    message_result = cursor.fetchone()
                cursor.execute("select OrganizationId, Name, Image, SectorId, ListedId, CountryId,StateId,CityId,Area,PinCode,NumberOfEmployee from Organization where OrganizationId = %s",[organization_id])
                organization_detail_list_by_id = cursor.fetchall()
                organization_detail_list = []
                for id,name,image,sector_id,listed_id,country_id,state_id,city_id,area,pincode,numberofemployee in organization_detail_list_by_id:
                    org = organization()
                    org.organization_name = name
                    org.organization_image = image
                    org.sector_id = sector_id
                    org.listed_id = listed_id
                    org.country_id = country_id
                    org.state_id = state_id
                    org.city_id = city_id
                    org.area = area
                    org.pincode = pincode
                    org.number_of_employee = numberofemployee
                    if message_result:
                        org.rejected_message = message_result[0]
                    # org.organization_verified = organization_verified_dict[id]
                    organization_detail_list.append(org.to_dict())
                res.organization_list = organization_detail_list
                res.user_id = user_id
                res.organization_id = organization_id
                res.organization_editable_data_send_succesfull = True
                return JsonResponse(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.organization_editable_data_send_succesfull = True
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.organization_editable_data_send_succesfull = True
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TerminateEmployeeAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                user_id = getattr(request, 'user_id', None)
                data = request.data
                organization_id = data.get('organization_id')
                employee_id = data.get('employee_id')
                logger.info(data)
                res = response()
                with connection.cursor() as cursor:
                    cursor.execute("Update EmployeeOrganizationMapping set StatusId = %s Where EmployeeId = %s and OrganizationId = %s",[2,employee_id,organization_id])
                    res.is_employee_terminated_successfull = True
                    res.user_id = user_id
                    res.organization_id = organization_id
                    res.employee_id = employee_id
                    return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_employee_terminated_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_terminated_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DocumentVerificationDataAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        logger.info(data)
        res = response()
        res.user_id = user_id
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT org.OrganizationId,org.Name,org.DocumentTypeId,org.DocumentNumber,org.DocumentFile,org.SectorId,org.ListedId,org.Image,org.CreatedOn,org.GSTIN,org.NumberOfEmployee,org.CountryId,org.StateId,org.CityId,org.Area,org.PinCode FROM [Organization] AS org JOIN [UserOrganizationMapping] AS uom ON org.OrganizationId = uom.OrganizationId WHERE uom.IsVerified = 0")
                rows = cursor.fetchall()
                organization_data = []
                if rows:
                    for row in rows:
                        org = organization()
                        org.organization_id = row[0]
                        org.name = row[1]
                        org.document_name = document_type_data[row[2]]['Name']
                        org.document_number = row[3]
                        org.document_file = row[4]
                        org.sector_name = sector_type_data[row[5]]['Name']
                        org.listed_name = listed_type_data[row[6]]['Name']
                        org.image = row[7]
                        org.date_time = convert_to_ist_time(row[8])
                        org.gstin = row[9]
                        org.number_of_employee = row[10]
                        org.country_name = country_data[row[11]]['Name']
                        org.state_name = state_data[row[12]]['Name']
                        org.city_name = city_data[row[13]]['Name']
                        org.area = row[14]
                        org.pincode = row[15]
                        organization_data.append(org.to_dict())
                    res.organization_verification = organization_data
                    res.is_document_verification_data_successfull = True
                else:
                    res.is_document_verification_data_successfull = False
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_document_verification_data_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_document_verification_data_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOrganizationAPIview(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get("user_id")
        organization_id = data.get('organization_id')
        approve = data.get('approve')
        rejected_message = data.get('message')
        logger.info(data)
        res = response()
        try:
            with connection.cursor() as cursor:
                if approve:
                    cursor.execute("update [UserOrganizationMapping] set Isverified = %s WHERE OrganizationId = %s",[1,organization_id])
                    res.is_organization_verified_successfull = True
                else:
                    cursor.execute("update [UserOrganizationMapping] set IsRejected = %s WHERE OrganizationId = %s",[1,organization_id])
                    if rejected_message is not None or len(rejected_message)>1:
                        cursor.execute("Insert into RejectMessage(UserId,OrganizationId,Message,CreatedOn) VALUES(%s,%s,%s,GETDATE())",[user_id,organization_id,rejected_message])
                    res.is_organization_rejected_successfull = True
                return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
                
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_organization_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_organization_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SubscribeAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        organization_id = data.get('organization_id')
        plan_id = data.get('plan_id')
        logger.info(data)
        res = response()
        pay = payment()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT RazorPaySubscriptionId from [Subscription] where UserId = %s and OrganizationId = %s and SubscriptionStatusId = 1 ",[user_id,organization_id]) # 1 created
                razor_pay_subscription_id_created_result = cursor.fetchone()
                cursor.execute("SELECT RazorPaySubscriptionId from [Subscription] where UserId = %s and OrganizationId = %s and SubscriptionStatusId != 1 ",[user_id,organization_id])
                razor_pay_subscription_id_completed_and_not_created_result = cursor.fetchone()
                subscription_response_list = []
                if razor_pay_subscription_id_created_result:
                    pay.subscription_id = razor_pay_subscription_id_created_result[0]
                    subscription_response_list.append(pay.to_dict())
                    res.subscription_response_list = subscription_response_list
                    res.is_subscription_id_already_exist = True
                elif razor_pay_subscription_id_completed_and_not_created_result is None or razor_pay_subscription_id_completed_and_not_created_result:
                    url = 'http://localhost:8081/razorpay/create/subscription'
                    data = {
                        'user_id': user_id,
                        'organization_id': organization_id,
                        'plan_id':plan_id,
                    }
                    response_data = requests.post(url, json=data)
                    if response_data.status_code == 200:
                        data = response_data.json()
                        subscriptionLink = data.get('subscriptionLink')
                        subscription_id = data.get('subscriptionId')
                        razor_pay_status = data.get('status')
                        pay.subscriptionLink = subscriptionLink
                        pay.subscription_id = subscription_id
                        pay.razor_pay_status = razor_pay_status
                        subscription_response_list.append(pay.to_dict())
                        res.subscription_response_list = subscription_response_list
                        res.is_subscription_id_created_successfull = True
                    else:
                        res.is_subscription_id_created_successfull = False
                else:
                    res.is_subscription_id_created_successfull = False
                return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_subscription_id_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_subscription_id_created_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPaymentAPIview(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        organization_id = data.get('organization_id')
        payment_id = data.get('payment_id')
        subscription_id = data.get('subscription_id')
        logger.info(data)
        res = response()
        pay = payment()
        try:
            url = 'http://localhost:8081/razorpay/verify/payment'
            data = {
                'user_id': user_id,
                'organization_id': organization_id,
                'payment_id' : payment_id,
                'subscription_id' : subscription_id,
            }
            response_data = requests.post(url, json=data)
            payment_response_list = []
            if response_data.status_code == 200:
                data = response_data.json()
                payment_status = data.get('Status')
                if payment_status == 'paid':
                    with connection.cursor() as cursor:
                        cursor.execute("Update UserOrganizationMapping set IsPaid = 1 where UserId = %s and OrganizationId = %s",[user_id,organization_id])
                        pay.payment_status = payment_status
                        pay.transaction = data.get('Transaction')
                elif payment_status == 'failed':
                    pay.payment_status = payment_status
                    pay.payment_cancelled = data.get('payment_cancelled')
                    pay.error_description = data.get('error_description')
                    pay.error_source = data.get('error_source')
                    pay.error_step = data.get('error_step')
                else:
                    pay.payment_status = payment_status
                    pay.transaction = data.get('Transaction')
                payment_response_list.append(pay.to_dict())
                res.payment_response_list = payment_response_list
                res.is_payment_response_sent_succefull = True
            else:
                res.is_payment_response_sent_succefull = False
            return Response(res.convertToJSON(), status = status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            logger.exception('Database integrity error: {}'.format(str(e)))
            res.is_payment_response_sent_succefull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.exception('An unexpected error occurred: {}'.format(str(e)))
            res.is_payment_response_sent_succefull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            


