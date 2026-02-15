from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


@csrf_protect
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "" or password == "":
            messages.error(request, "Username and password are required.")
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
            return redirect(reverse('homecontrol:dashboard'))
        else:
            messages.error(request, "Username and password are required.")
            return render(request, 'login.html')    
    else:
        return render(request, 'login.html', context={})

def user_logout(request):
    logout(request)
    return redirect(reverse('accounts:login'))



