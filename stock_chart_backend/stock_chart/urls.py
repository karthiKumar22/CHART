from django.urls import path
from . import views

app_name = 'stock_chart'  # This sets the namespace for the URLs in this app

urlpatterns = [
    path('', views.home, name='home'),
    path('display_ticker/<str:ticker>/', views.display_ticker, name='display_ticker'),
    path('update_data/<str:ticker>/<str:interval>/', views.update_data, name='update_data'),
    path('search_stocks/', views.search_stocks, name='search_stocks'),
    path('manage_watchlist/', views.manage_watchlist, name='manage_watchlist'),
    path('update_watchlist_data/', views.update_watchlist_data, name='update_watchlist_data'),
]

