# activities/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- 1. Web Views (Fellows) ---
    path('submit/', views.submit_activity_view, name='submit_activity'),
    path('edit/<int:pk>/', views.edit_report_view, name='edit_report'),
    path('dashboard/', views.fellow_dashboard_view, name='fellow_dashboard'),
    path('all-activities/', views.all_activities_view, name='all_activities'),
    path('activity/<int:pk>/', views.activity_detail_view, name='activity_detail'),

    # --- 2. Web Views (Mentors) ---
    path('mentor/dashboard/', views.mentor_dashboard_view, name='mentor_dashboard'),
    path('review/<int:pk>/', views.review_report_view, name='review_report'),
    
    # --- 3. Reporting (HTML/File Downloads) ---
    path('summary/', views.impact_summary, name='impact_summary'),
    path('export/csv/', views.export_activities_csv, name='api-export-csv'),
]