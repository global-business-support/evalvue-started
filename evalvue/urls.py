from django.contrib import admin
from django.urls import path,include
from info import urls
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('info.urls')),
    
]
