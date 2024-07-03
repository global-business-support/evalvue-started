from django.contrib import admin
from django.urls import path
from .views import DocumentVerificationDataAPIview, SubscribeAPIview, TopFiveEmployeeAPIview,EditOrganizationAPIview,EditEmployeeAPIview, VerifyOrganizationAPIview
from .views import CreateEmployeeAPIView, CreateReviewAPIView, CreateUserAPIView, DashboardFeedAPIview, EmployeeAPIView, EmployeeEditableDataAPIView, OrganizationEditableDataAPIView, SearchByAadharAPIview, ShootOtpAPIView, LoginUserAPIView, ReviewAPIView, TerminateEmployeeAPIView, UpdatePasswordAPIView, VerifyOtpAPIView,OrganizationAPIView,CreateOrganizationAPIview,AddOrganizationAPIview
urlpatterns = [
    path('create/user/', CreateUserAPIView.as_view(), name='create_user'),
    path('employees/', EmployeeAPIView.as_view(), name='employees'),
    path('create/employees/',CreateEmployeeAPIView.as_view(), name='create_employees'),
    path('login/user/',LoginUserAPIView.as_view(), name='login_user'),
    path('create/review/',CreateReviewAPIView.as_view(), name='create_review'),
    path('reviews/',ReviewAPIView.as_view(), name='reviews'),
    path('shoot/otp/',ShootOtpAPIView.as_view(), name='shoot_otp'),
    path('verify/otp/',VerifyOtpAPIView.as_view(), name='verify_otp'),
    path('update/password/',UpdatePasswordAPIView.as_view(), name='update_password'),
    path('create/organization/',CreateOrganizationAPIview.as_view(), name='create_organization'),
    path('organizations/',OrganizationAPIView.as_view(), name='organizations'),
    path('add/organization/',AddOrganizationAPIview.as_view(), name='add_organization'),
    path('dashboard/feed/',DashboardFeedAPIview.as_view(), name='dashboard_feed'),
    path('search/employee/aadhar/',SearchByAadharAPIview.as_view(), name='search_employee_aadhar'),
    path('top/employee/', TopFiveEmployeeAPIview.as_view(), name = 'top_employee'),
    path('organization/edit/', EditOrganizationAPIview.as_view(), name = "organization_edit"),
    path('employee/edit/',EditEmployeeAPIview.as_view(), name = 'employee_edit'),
    path('employee/editable/data/',EmployeeEditableDataAPIView.as_view(), name='employee_editable_data'),
    path('organization/editable/data/',OrganizationEditableDataAPIView.as_view(), name='organization_editable_data'),
    path('terminate/employee/',TerminateEmployeeAPIView.as_view(), name='terminate_employee'),
    path('document/verification/data/', DocumentVerificationDataAPIview.as_view(), name = 'document_verification_data'),
    path('verify/organization/', VerifyOrganizationAPIview.as_view(), name = 'verify_organization'),
    path('create/subscription/id/', SubscribeAPIview.as_view(), name = 'create_subscription_id')


]