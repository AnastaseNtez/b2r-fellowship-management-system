from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Explicitly import the views to match your views.py logic
from .views import (
    submit_activity_view, 
    review_report_view, 
    mentor_dashboard_view,
    DashboardStatsAPIView,
    export_activities_csv,
    TrainingActivityViewSet
)

# Router for TrainingActivity API endpoints
router = DefaultRouter()
router.register(r'logs', TrainingActivityViewSet, basename='trainingactivity')

urlpatterns = [
    # --- 1. Standard Web Views ---
    # View for Fellows to log sessions
    path('submit/', submit_activity_view, name='submit_activity'),

    # View for Mentors to see their assigned tasks
    path('mentor/dashboard/', mentor_dashboard_view, name='mentor_dashboard'),

    # View for Mentors to Approve/Reject specific reports
    path('review/<int:pk>/', review_report_view, name='review_report'),
    
    # --- 2. Reporting & Data Exports ---
    # CSV download for donors and admins
    path('export/csv/', export_activities_csv, name='export_activities_csv'),

    # --- 3. API Endpoints ---
    # High-level metrics for the analytics dashboard
    path('api/summary/', DashboardStatsAPIView.as_view(), name='api_dashboard_summary'),

    # Automatic REST routes for logs
    path('api/', include(router.urls)), 

    path('edit/<int:pk>/', views.edit_report_view, name='edit_report'),
    
    path('approve/<int:pk>/', views.approve_report, name='approve_report'),

    path('fellow/all-activities/', views.all_activities_view, name='all_activities'),
]