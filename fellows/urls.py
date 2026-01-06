from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# This creates endpoints like /api/fellows/ and /api/fellows/statistics/
router.register(r'', views.FellowViewSet, basename='fellow')

urlpatterns = [
    
    # API end points
    # These will be accessible at api/fellows/register/ and api/fellows/dashboard/  end points
    path('register/', views.fellow_register_view, name='fellow_register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # This becomes: /fellows/
    path('', views.fellow_list_view, name='fellow_list'),
    
    # This becomes: /fellows/add/
    path('add/', views.fellow_create_view, name='fellow_create'),
    
    # This becomes: /fellows/13/edit/
    path('<int:pk>/edit/', views.fellow_edit_view, name='fellow_edit'),
    
    # This becomes: /fellows/13/delete/
    path('<int:pk>/delete/', views.fellow_delete_view, name='fellow_delete'),
]