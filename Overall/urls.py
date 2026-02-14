
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),


     # custom login/logout
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Allauth URLs
    path('accounts/', include('allauth.urls')),
    
    path('', include('homecontrol.urls')),
    path('chat/', include('chat.urls')),
    path('finance/', include('finance.urls')),

]
