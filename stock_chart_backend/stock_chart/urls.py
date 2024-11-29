from django.urls import path
from . import views

app_name = 'stock_chart'

urlpatterns = [
    path('ticker/<str:ticker>/', views.display_ticker, name='display_ticker'),
    path('update_data/<str:ticker>/<str:interval>/', views.update_data, name='update_data'),
]