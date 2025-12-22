from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect



@csrf_protect
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "" or password == "":
            messages.error(request, "Username and password are required.")
            return render(request, 'login.html', context=context)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('homecontrol:dashboard'))
        else:
            context = {
                'error': 'Invalid username or password'
            }
            return render(request, 'login.html', context=context)    
    else:
        return render(request, 'login.html', context={})

def user_logout(request):
    logout(request)
    return redirect(reverse('homecontrol:login'))



@login_required(login_url='homecontrol:login')
def dashboard(request):
    context = {}
    messages.success(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
    messages.error(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
    messages.warning(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
    messages.info(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
    return render(request, 'index/dashboard.html', context=context)
