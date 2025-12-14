from django.urls import path, include
from rest_framework import routers 

# The router will be used for UserProfile/Account management APIs later
router = routers.DefaultRouter()
# router.register(r'profiles', views.UserProfileViewSet) 

urlpatterns = [
    # Placeholder for REST Framework's default login/logout views (optional, but standard)
    # path('', include(router.urls)), 

    # will use this path for JWT login/token endpoints later
    # path('login/', views.LoginView.as_view(), name='auth_login'), 
    
    # Minimal URL set to fix the import error:
    path('', include(router.urls)),
]