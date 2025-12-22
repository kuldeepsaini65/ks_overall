from django.urls import path, include
from django.contrib import admin
from homecontrol import views as home_views


app_name = 'homecontrol'

urlpatterns = [
    path('', home_views.dashboard, name='dashboard'),  
    path('login/', home_views.user_login, name='login'),
    path('logout/', home_views.user_logout, name='logout'),
]