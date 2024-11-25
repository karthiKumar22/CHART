# stock_chart/urls.py
from django.urls import path
from .views import display_ticker

app_name = 'stock_chart'  # This is the namespace for the app

urlpatterns = [
    path('ticker/<str:ticker>/', display_ticker, name='display_ticker'),  # Correctly defined URL pattern
]