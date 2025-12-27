# fellows/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 
from .views import fellow_register_view, dashboard_view # Add dashboard_view

router = DefaultRouter()
# If I eventually register the FellowViewSet, it will look like this:
# router.register(r'', views.FellowViewSet) 

urlpatterns = [
    path('register/', views.fellow_register_view, name='fellow_register'), 

    # Rename 'fellow_dashboard' to 'dashboard' 
    # This must match LOGIN_REDIRECT_URL = 'dashboard' in settings.py
    path('dashboard/', views.dashboard_view, name='dashboard'), 

    path('', include(router.urls)), 
]