from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('app.users.urls')),
    path('products/', include('app.products.urls')),
    path('campaigns/', include('app.campaigns.urls')),
    path('appointments/', include('app.appointments.urls')),
]
