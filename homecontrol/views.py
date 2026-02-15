from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required



@login_required(login_url='accounts:login')
def dashboard(request):
    context = {}
    return render(request, 'index/dashboard.html', context=context)
