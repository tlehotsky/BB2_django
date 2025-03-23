#boatbrain/urls.py
from django.urls import path
from .views import home_page_view, log_page_view, current_trip_page_view, about_page_view  # Import the home view

urlpatterns = [
    path('', home_page_view, name='home'),  # Ensure this exists
    path('log/', log_page_view, name='log'),
    path('current-trip/', current_trip_page_view, name='current_trip'),
    path('about/', about_page_view, name='about'),
]
