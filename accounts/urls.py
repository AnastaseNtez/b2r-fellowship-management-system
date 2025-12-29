from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import RegisterView, smart_redirect

urlpatterns = [
    # --- JWT AUTHENTICATION ENDPOINTS ---
    
    # URL: POST /api/auth/register/
    # Description: Creates a new User account. Requires username, password, and email.
    path('register/', RegisterView.as_view(), name='api_register'),
    
    # URL: POST /api/auth/login/
    # Description: Exchange credentials for Access and Refresh tokens.
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # URL: POST /api/auth/logout/
    # Description: Blacklists the Refresh token to securely end the session.
    # Note: Requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS.
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # URL: POST /api/auth/token/refresh/
    # Description: Generates a new Access token using a valid Refresh token.
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- WEB & UTILITY ENDPOINTS ---
    
    # URL: GET /api/auth/redirect/
    # Description: Internal gatekeeper that routes users to their specific dashboard based on Role.
    path('redirect/', smart_redirect, name='smart_redirect'), 
]