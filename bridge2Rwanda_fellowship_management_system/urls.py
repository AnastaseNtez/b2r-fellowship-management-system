from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import smart_redirect # Import the gatekeeper view

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- GATEKEEPER: The Main Entry Point ---
    # This ensures that when a user visits http://127.0.0.1:8000/, 
    # they are automatically checked for a role and redirected.
    path('', smart_redirect, name='index'),

    # --- Web Authentication (Login/Logout) ---
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 1. Authentication App Logic
    path('accounts/', include('accounts.urls')), 
    
    # 2. Locations AJAX URLs
    path('locations/', include('locations.urls')), 
    
    # 3. FELLOWS APP - WEB VIEWS
    path('fellows/', include('fellows.urls')),

    # 4. FELLOWS APP - API ENDPOINTS
    path('api/fellows/', include('fellows.urls')),
    
    # 5. Activities App URLs
    path('activities/', include('activities.urls')), # Web views for submitting reports
    path('api/activities/', include('activities.urls')), # API endpoints

    # 6. Mentors App URLs
    path('mentors/', include('mentors.urls')),

]

# --- Static and Media Files ---
# This allows Django to serve images (like training photos) during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)