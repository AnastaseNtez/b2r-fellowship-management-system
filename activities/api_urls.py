# activities/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'logs', views.TrainingActivityViewSet, basename='trainingactivity')

urlpatterns = [
    # API endpoints used by Dashboard JS or Mobile Apps
    path('dashboard/', views.DashboardStatsAPIView.as_view(), name='api-dashboard'),
    path('impact/', views.ImpactReportDataAPIView.as_view(), name='api-impact'),
    path('fellow-performance/', views.FellowPerformanceAPIView.as_view(), name='api-performance'),
    
    # The ModelViewSet routes (e.g., /api/activities/logs/)
    path('', include(router.urls)), # logs of training activity
]