
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homecontrol.urls')),
    path('chat/', include('chat.urls')),
    path('finance/', include('finance.urls')),

]
