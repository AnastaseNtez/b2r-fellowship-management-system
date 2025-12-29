from django.urls import path
from . import views

urlpatterns = [
    # 1.REST API Paths (Required for Capstone)
    path('provinces/', views.ProvinceListView.as_view(), name='api-provinces'),
    path('districts/', views.DistrictListView.as_view(), name='api-districts'),
    path('sectors/', views.SectorListView.as_view(), name='api-sectors'),
    path('sectors/<int:id>/coverage/', views.SectorCoverageAPIView.as_view(), name='api-sector-coverage'),

    # 2. Existing AJAX Paths (Required for your HTML Forms)
    path('ajax/load-districts/', views.load_districts, name='ajax_load_districts'),
    path('ajax/load-sectors/', views.load_sectors, name='ajax_load_sectors'),
]