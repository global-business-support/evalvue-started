def save_image(path,image):
    image_path = path + image.name
    with open(image_path, 'wb') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    return image_path 



from django.db import connection,IntegrityError,transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
def send_email(to_email,otp_number):
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # cursor.execute("INSERT into [OTP] (Email, OtpNumber, Is_Verified, CreatedOn) VALUES(%s,%s,%s,GETDATE())",[to_email, otp_number,False])
                msg =  render_to_string('info/email_template.html',{'otp_number': otp_number})
                
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
