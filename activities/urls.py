# activities/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import submit_activity_view, review_report_view # Import your custom views
 

# Router for TrainingActivity API endpoints
router = DefaultRouter()

urlpatterns = [
    # 1. Standard Web Views
    path('submit/', submit_activity_view, name='submit_activity'),
    
    path('review/<int:pk>/', review_report_view, name='review_report'), # New path
    
    # 2. API Endpoints (e.g., /api/activities/)
    path('api/', include(router.urls)), # Changed to 'api/' to avoid conflict with 'submit/'
]