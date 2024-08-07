import re
from django.db import connection,IntegrityError,transaction
from .cache import *


def validate_name(name):
    if re.match(r"^(?=.{2,50}$)[a-zA-Z]+(?:[ '-][a-zA-Z]+)*$",name.strip()):
        return True
    return False

def validate_mobile_number(mobile_number):
    if re.match(r'^\d{10}$', mobile_number.strip()):
        return True
    return False

def validate_email(email):
    if re.match(r'^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email.strip()):
        return True
    return False

def validate_designation(designation):
    if re.match(r"^[a-zA-Z\s.,&()-]{1,50}$",designation.strip()):
        return True
    return False

def validate_password(password):
    if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$', password.strip()):
        return True
    return False

def validate_aadhar_number(aadhar_number):
    if re.match(r"^\d{12}$",aadhar_number.strip()):
        return True
    return False

def validate_comment(comment):
    if re.match(r'(?s)^.{250,500}$',comment.strip()):
        return True
    return False

def validate_otp(otp_number):
    if re.match(r'^\d{6}$',otp_number.strip()):
        return True
    return False

def validate_organization_name(organization_name):
    if re.match(r"^.{1,50}$",organization_name.strip()):
        return True
    return False

def validate_document_number(document_number):
    if len(document_number.strip())<=50:
        return True
    return False

def validate_pin_code(pincode):
    if re.match(r"^[1-9][0-9]{5}$",pincode.strip()):
        return True
    return False

def validate_gstin(gstin):
    if gstin is None or len(gstin)<1:
        return True
    if re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$",gstin.strip()):
        return True
    return False

def validate_referral_code(referral_code):
    if referral_code is None or len(referral_code)<1:
        return True
    if re.match(r"^EV[A-Z]{2}\d{2}$",referral_code.strip()) and referral_code in referral_codes_data:
        return True
    return False

    