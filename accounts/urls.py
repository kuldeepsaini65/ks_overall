from accounts.views import user_login, user_logout
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
