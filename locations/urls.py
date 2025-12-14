from django.urls import path
from . import views

urlpatterns = [
    path('ajax/load-districts/', views.load_districts, name='ajax_load_districts'),
    path('ajax/load-sectors/', views.load_sectors, name='ajax_load_sectors'),
]