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
from django.db import connection,IntegrityError # Import IntegrityError for database integrity violations
from .response import *


#creating user in user table
class CreateUserAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        try:
            # Get data from the request
            data = request.data
            name = data.get('name')
            email = data.get('email')
            mobile_number = data.get('mobile_number')
            password = data.get('password')

            res = response()
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
                    cursor.execute("INSERT INTO [User] (Name, Email, MobileNumber, Password) VALUES (%s, %s, %s, %s)",
                                [name, email, mobile_number, password]) 
                    
                
                if not res.is_user_register_successfull:
                    return Response(res.convertToJSON(), status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(res.convertToJSON(), status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            print('Database integrity error: {}'.format(str(e)))
            res.is_user_register_successfull = False
            res.error = 'Something went wrong , Please try after sometime'
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print('An unexpected error occurred: {}'.format(str(e)))
            res.is_user_register_successfull = False
            res.error = 'Something went wrong , Please try after sometime'
            return Response(res.convertToJSON(), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

