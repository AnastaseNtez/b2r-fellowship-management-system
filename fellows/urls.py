from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# This creates endpoints like /api/fellows/ and /api/fellows/statistics/
router.register(r'', views.FellowViewSet, basename='fellow')

urlpatterns = [
    # API Routes (Must come before specific paths if using empty string router)
    path('', include(router.urls)),

    # Web/Browser Routes
    # These will be accessible at api/fellows/register/ and api/fellows/dashboard/
    path('register/', views.fellow_register_view, name='fellow_register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]