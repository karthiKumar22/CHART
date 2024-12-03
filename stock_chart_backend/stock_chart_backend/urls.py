# stock_chart_backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_chart.urls')),  # Assuming 'stock_chart' is your app name
]