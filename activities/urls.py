# activities/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Router for TrainingActivity API endpoints
router = DefaultRouter()

urlpatterns = [
    # API Endpoints (e.g., /api/activities/)
    path('', include(router.urls)),
]