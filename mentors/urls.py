from django.urls import path
from .views import mentor_register_view, mentor_dashboard, review_activity

urlpatterns = [
    # Path for creating new mentors (used by Coordinator)
    path('register/', mentor_register_view, name='mentor_register'),
    
    # Path for the Mentor's private portal
    path('dashboard/', mentor_dashboard, name='mentor_dashboard'),
    
    # Path for reviewing a specific activity report (uses the report ID)
    path('review/<int:pk>/', review_activity, name='review_report'),
]