from django.urls import path
from .views import login, RegisterView

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]