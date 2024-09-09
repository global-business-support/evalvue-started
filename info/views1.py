from django.http import JsonResponse
import os 
import jwt
import pytz
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status
import requests
from django.db import connection,IntegrityError,transaction
from evalvue import settings
import logging

logger = logging.getLogger('info')






