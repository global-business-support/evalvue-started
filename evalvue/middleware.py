from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication, JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        open_paths = ['/login/user/','/create/user/','/employees/','/create/employees/','/reviews/','/shoot/otp/','/verify/otp/','/update/password/','/create/organization/','/organizations/','/dashboard/feed/','/add/organization/','/dashboard/feed/','/search/employee/aadhar/']

        if request.path in open_paths:
            return None

        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is None:
            return JsonResponse({'error': 'Unauthorized: Missing Authorization Header'}, status=401)

        try:
            token = auth_header.split()[1]
            jwt_auth = JWTStatelessUserAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            user_id = user.user_id
            request.user_id = user_id
        except (InvalidToken, TokenError, jwt.ExpiredSignatureError, jwt.DecodeError) as e:
            return JsonResponse({'error': 'Unauthorized', 'details': str(e)}, status=401)

        return None
