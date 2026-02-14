from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required(login_url='accounts:login')
def dashboard(request):
    context = {}
    messages.success(request, f"Welcome back, {request.user.username}! You have successfully logged in.")
    return render(request, 'index/dashboard.html', context=context)
