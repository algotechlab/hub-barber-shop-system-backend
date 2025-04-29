# src/apps/users/views.py
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import User
from django.urls import reverse_lazy

class RegisterView(CreateView):
    model = User
    fields = ['name', 'email', 'password', 'phone']
    template_name = 'pages/login/register.html'
    success_url = reverse_lazy('users:login')


def login(request):
    return render(request, 'pages/login/login.html', {'register': False})


def register(request):
    return render(request, 'pages/login/register.html', {'register': True})
