# src/apps/users/views.py
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegisterForm

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'pages/login/register.html'
    success_url = reverse_lazy('users:login')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # return redirect('users:dashboard')  # Redirecionar para o dashboard ou home
        else:
            return render(request, 'pages/login/login.html', {'error': 'Credenciais inválidas'})
    return render(request, 'pages/login/login.html')

