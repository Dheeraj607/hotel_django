from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('hotel_app.urls')),  # Your API endpoints will be under /api/
]
