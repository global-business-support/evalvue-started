import re

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

def validate_password(password):
    if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$', password.strip()):
        return True
    return False

def validate_aadhar_number(aadhar_number):
    if re.match(r"^\d{12}$",aadhar_number.strip()):
        return True
    return False

def validate_comment(comment):
    if re.match(r'^[a-zA-Z0-9\s\.\-\_\!\?\'"]{300,500}$',comment.strip()):
        return True
    return False

def validate_otp(otp_number):
    if re.match(r'^\d{6}$',otp_number.strip()):
        return True
    return False

def validate_organization_name(organization_name):
    if re.match(r"^(?=.{2,50}$)[a-zA-Z0-9&.,'\-() ]+$",organization_name.strip()):
        return True
    return False

