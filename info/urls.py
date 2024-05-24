from django.contrib import admin
from django.urls import path
from .views import CreateEmployeeAPIView, CreateReviewAPIView, CreateUserAPIView, EmployeeAPIView, ForgotPasswordAPIView, LoginUserAPIView, MyDataView, ReviewAPIView, UpdatePasswordAPIView, VerifyOtpAPIView,OrganizationAPIView,CreateOrganizationAPIview,AddOrganizationAPIview
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('create/user/', CreateUserAPIView.as_view(), name='create_user'),
    path('employees/', EmployeeAPIView.as_view(), name='employees'),
    path('create/employees/',CreateEmployeeAPIView.as_view(), name='create_employees'),
    path('login/user/',LoginUserAPIView.as_view(), name='login_user'),
    path('create/review/',CreateReviewAPIView.as_view(), name='create_review'),
    path('reviews/',ReviewAPIView.as_view(), name='reviews'),

    path('forgot/password/',ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('verify/otp/',VerifyOtpAPIView.as_view(), name='verify_otp'),
    path('update/password/',UpdatePasswordAPIView.as_view(), name='update_password'),
    path('create/organization/',CreateOrganizationAPIview.as_view(), name='create_organization'),
    path('organizations/',OrganizationAPIView.as_view(), name='organizations'),
    path('add/organization/',AddOrganizationAPIview.as_view(), name='add_organization'),

    path('cache/data/', MyDataView.as_view(), name='data-view'),





]