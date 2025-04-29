from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]



"""
path('users/', include('apps.users.urls')),
path('products/', include('apps.products.urls')),
path('campaigns/', include('apps.campaigns.urls')),
path('appointments/', include('apps.appointments.urls')),
"""