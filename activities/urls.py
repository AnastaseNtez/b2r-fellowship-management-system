from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 1. Setup the Router
router = DefaultRouter()
router.register(r'logs', views.TrainingActivityViewSet, basename='trainingactivity')

urlpatterns = [
    # --- 1. Web Views (Fellows) ---
    path('submit/', views.submit_activity_view, name='submit_activity'),
    path('edit/<int:pk>/', views.edit_report_view, name='edit_report'),
    path('dashboard/', views.fellow_dashboard_view, name='fellow_dashboard'),
    path('fellow/all-activities/', views.all_activities_view, name='all_activities'),

    # --- 2. Web Views (Mentors) ---
    path('mentor/dashboard/', views.mentor_dashboard_view, name='mentor_dashboard'),
    path('review/<int:pk>/', views.review_report_view, name='review_report'),
    
    # --- 3. Reporting & Analytics ---
    path('summary/', views.impact_summary, name='impact_summary'),
    
    # FIX: Restoring 'api-export-csv' name for the template
    path('export/csv/', views.export_activities_csv, name='api-export-csv'), # Ensure this name matches
    # Also keeping the other name just in case
    path('reports/export/csv/', views.export_activities_csv, name='export_activities_csv'),

    # --- 4. API Endpoints (Used by Dashboard JS) ---
    path('reports/dashboard/', views.DashboardStatsAPIView.as_view(), name='api-dashboard'),
    path('reports/impact/', views.ImpactReportDataAPIView.as_view(), name='api-impact'),
    path('reports/fellow-performance/', views.FellowPerformanceAPIView.as_view(), name='api-performance'),

    # --- 5. The API Router ---
    path('', include(router.urls)), 
]