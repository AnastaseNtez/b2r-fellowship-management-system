from django.urls import path, include
from rest_framework import routers 
from .views import smart_redirect, UserProfile # Add your login/logout views if they are here

# The router will be used for UserProfile/Account management APIs later
router = routers.DefaultRouter()
# router.register(r'profiles', views.UserProfileViewSet) 

urlpatterns = [
    # This 'name' must match LOGIN_REDIRECT_URL in settings.py
    path('redirect/', smart_redirect, name='smart_redirect'), 
    
    # Minimal URL set to fix the import error:
    path('', include(router.urls)),
]