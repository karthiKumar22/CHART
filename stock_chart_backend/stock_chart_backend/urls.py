# stock_chart_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from stock_chart.views import home  # Import the home view for redirection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Redirect root URL to the home view
    path('', include('stock_chart.urls')),  # Include stock_chart app URLs
]