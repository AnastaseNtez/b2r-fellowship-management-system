# fellows/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 
from .views import fellow_register_view, dashboard_view # Add dashboard_view

router = DefaultRouter()
# If I eventually register the FellowViewSet, it will look like this:
# router.register(r'', views.FellowViewSet) 

urlpatterns = [
    # This maps to the /register/ part of the URL (e.g., /fellows/register/)
    path('register/', views.fellow_register_view, name='fellow_register'), 

    # This handles the API requests (e.g., /api/fellows/)
    path('', include(router.urls)), 
    
    path('dashboard/', dashboard_view, name='dashboard'), # Dashboard URL
]