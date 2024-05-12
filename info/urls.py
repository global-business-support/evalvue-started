from django.contrib import admin
from django.urls import path
from .views import CreateUserAPIView
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('createUser/', CreateUserAPIView.as_view(), name='createUser'),

]