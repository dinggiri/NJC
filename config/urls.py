from django.contrib import admin
from django.urls import path, include
from k99 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('k99/', include('k99.urls')),
    path('', include('common.urls')),
]