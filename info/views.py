from django.shortcuts import render,redirect
from django.http import JsonResponse
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
from info import review
from info.constant import *
from info.utility import hash_password, save_image, send_email, verify_password
from .employee import *
from .response import *
from .review import *


#creating user in user table
class CreateUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
            # Get data from the request
                data = request.data
                name = data.get('name')
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                password = data.get('password')
                res.is_user_register_successfull = True
                
                # Validate data using regex
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

                # Save data to user table
                with connection.cursor() as cursor:
                    cursor.execute("Select count(UserId) from [User] where Email = %s or MobileNumber = %s",[email,mobile_number])
                    count = cursor.fetchone()[0]
                    if count > 0:
                        res.is_user_register_successfull = False
                        res.error = 'User Alreary Exists with this Email and Mobile Number'
                    else:
                        password = hash_password(password, salt)
                        cursor.execute("INSERT INTO [User] (Name, Email, MobileNumber, Password, CreatedOn) VALUES (%s, %s, %s, %s,GETDATE())",
                                    [name, email, mobile_number, password]) 
                        
                    
                    if not res.is_user_register_successfull:
                        return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_user_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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
                res.is_employee_mapped_to_organization_successfull = False
                
                with connection.cursor() as cursor:
                    cursor.execute("select EmployeeId from EmployeeOrganizationMapping where OrganizationId = %s",[organization_id])
                    employee_id_results = cursor.fetchall()
                    if employee_id_results:
                        employee_list = []
                        for employee_id_result in employee_id_results:
                            employee_id = employee_id_result[0]
                            cursor.execute("SELECT EmployeeId, Name, Email, MobileNumber, Image, AadharNumber FROM Employee WHERE EmployeeId = %s", [employee_id])
                            employee_details = cursor.fetchall()
                            for emp_id,emp_name,emp_email,emp_mobile,emp_image,emp_aadhar in employee_details:
                                emp = employee()
                                emp.employee_id = emp_id
                                emp.aadhar_number = emp_aadhar
                                emp.employee_image = emp_image
                                emp.employee_name = emp_name
                                emp.email = emp_email
                                emp.mobile_number = emp_mobile
                                employee_list.append(emp.to_dict())
                        res.is_employee_mapped_to_organization_successfull = True                    
                        res.user_id = user_id
                        res.organization_id=organization_id
                        res.employee_list = employee_list
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)
            
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_employee_mapped_to_organization_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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
                employee_name = data.get('employee_name')
                employee_image = data.get('employee_image')
                aadhar_number = data.get('aadhar_number')
                email = data.get('email')
                mobile_number = data.get('mobile_number')
                designation = data.get('designation')

                res.is_employee_register_successfull = False
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
                        employee_image = save_image(employee_image_path,employee_image)
                        cursor.execute("INSERT INTO Employee (Name, Email, MobileNumber, Image, AadharNumber, Designation, CreatedOn) VALUES (%s, %s, %s, %s, %s,%s, GETDATE())",[employee_name, email, mobile_number, employee_image, aadhar_number, designation])
                        cursor.execute("SELECT EmployeeId FROM Employee where AadharNumber = %s",[aadhar_number])
                        employee_id_for_organization_mapping = cursor.fetchone()[0]
                        cursor.execute("INSERT into EmployeeOrganizationMapping(EmployeeId,OrganizationId,StatusId,CreatedOn) values(%s,%s,%s,GETDATE())",[employee_id_for_organization_mapping,organization_id,1])
                        res.is_employee_register_successfull = True
                    res.user_id = user_id
                    res.organization_id = organization_id
                    return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_employee_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
            res.is_employee_register_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        res = response()
        try:
            with transaction.atomic():
                email = request.data.get('email')
                password = request.data.get('password')
                res.is_login_successfull = True
                if not email or not password:
                    res.is_login_successfull = False
                    res.error = 'Email and password are required'
                    # return JsonResponse({'error': 'Email and password are required'}, status=400)
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT UserId, Password FROM [User] WHERE Email = %s", [email])
                        user_details = cursor.fetchone()
                        if user_details :
                            user_id = user_details[0]
                            stored_password = user_details[1]
                            ok = verify_password(stored_password, password, salt)
                            if ok:
                                res.user_id = user_id
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
            print('Database integrity error: {}'.format(str(e)))
            res.is_login_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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
                with connection.cursor() as cursor:
                    cursor.execute("INSERT into Review(Comment, Image, Rating, CreatedOn) values(%s,%s,%s, GETDATE())",[comment,image,rating])
                    cursor.execute("SELECT max(ReviewId) from Review")
                    review_id_inserted_row = cursor.fetchone()
                    if review_id_inserted_row:
                        review_id = review_id_inserted_row[0]
                        cursor.execute("INSERT into ReviewEmployeeOrganizationMapping(ReviewId, OrganizationId, EmployeeId, CreatedOn) values(%s,%s,%s,GETDATE())",[review_id,organization_id,employee_id])
                        # review_employee_organization_mapped = cursor.fetchone()
                        # if review_employee_organization_mapped:
                    res.is_review_added_successfull = True
                    res.user_id = user_id
                    res.organization_id = organization_id
                    res.employee_id = employee_id
                    return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_review_added_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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

                    cursor.execute("SELECT ReviewId from ReviewEmployeeOrganizationMapping Where EmployeeId = %s",[employee_id])
                    review_id_results = cursor.fetchall()
                    if review_id_results:
                        review_list = []
                        for review_id_result in review_id_results:
                            review_id = review_id_result[0]
                            cursor.execute("SELECT ReviewId, Comment, Image, Rating from Review where ReviewId = %s",[review_id])
                            reviews_details = cursor.fetchall()
                            for rev_id, rev_comment, rev_image, rev_rating in reviews_details:
                                rev = review()
                                rev.review_id = rev_id
                                rev.comment = rev_comment
                                rev.image = rev_image
                                rev.rating = rev_rating
                                review_list.append(rev.to_dict())
                        res.is_review_mapped_to_employee_successfull = True
                        res.employee_list = employee_list
                        res.review_list = review_list
                        res.employee_id = employee_id
                        res.user_id = organization_id
                        res.organization_id = organization_id
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_review_mapped_to_employee_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
            res.is_review_mapped_to_employee_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgotPasswordAPIView(APIView):
    @csrf_exempt
    def post(self,request):
        res = response()
        try:
            with transaction.atomic():
                data = request.data 
                email = data.get("email")
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

                            ok = send_email(email_result[1],otp_number)
                            if ok:
                                res.otp_send_successfull = True
                                res.user_id = email_result[0]
                                res.email = email_result[1]
                return Response(res.convertToJSON(), status=status.HTTP_200_OK)
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.otp_send_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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
                res.otp_verified_successfull = False
                with connection.cursor() as cursor:
                    cursor.execute("SELECT OtpNumber,CreatedOn from OTP where email = %s ORDER BY CreatedOn desc",[email])
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
                            res.user_id = user_id
                    return Response(res.convertToJSON(), status=status.HTTP_200_OK)

        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.otp_verified_successfull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
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
                res.password_updated_successFull = False

                if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$', password):
                    res.password_updated_successFull = False
                    res.error = 'Invalid password'
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE [User] SET Password = %s, ModifiedOn = GETDATE() where UserId = %s",[password,user_id])
                        res.password_updated_successFull = True
                return Response(res.convertToJSON(), status = status.HTTP_200_OK)
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.password_updated_successFull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
            res.password_updated_successFull = False
            res.error = generic_error_message
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from info.cache import *

class MyDataView(APIView):
    def get(self, request):
        data = get_cached_review_data()
        if data:
            return Response(data)
        return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
        
