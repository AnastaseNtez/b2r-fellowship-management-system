from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),

    # 1. Authentication API
    path('api/auth/', include('accounts.urls')), 
    
    # 2. Locations AJAX URLs
    path('', include('locations.urls')), 
    
    # 3. FELLOWS APP - WEB VIEWS
    # This path handles web views like the registration form at /fellows/register/
    path('fellows/', include('fellows.urls')),

    # 4. FELLOWS APP - API ENDPOINTS
    # This path handles API endpoints like /api/fellows/
    path('api/fellows/', include('fellows.urls')),
    
    # 5. Activities App URLs
    path('api/activities/', include('activities.urls')),
    
    # ... other app includes (Reports, etc.)
]