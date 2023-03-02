from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.title, name='title'),
    path('login/', auth_views.LoginView.as_view(template_name='common/Login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]