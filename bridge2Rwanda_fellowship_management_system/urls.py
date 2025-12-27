from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import smart_redirect # Import the gatekeeper view

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- GATEKEEPER: The Main Entry Point ---
    # Redirects logged-in users to their respective dashboards
    path('', smart_redirect, name='smart_redirect'),

    # --- Web Authentication (Login/Logout) ---
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 1. Authentication App Logic
    path('accounts/', include('accounts.urls')), 
    
    # 2. Locations AJAX URLs
    path('locations/', include('locations.urls')), 
    
    # 3. FELLOWS APP - WEB VIEWS & DASHBOARD
    # This inclusion makes the 'dashboard' name available globally
    path('fellows/', include('fellows.urls')),
    
    # 4. Activities App URLs
    # Includes 'mentor_dashboard' and 'submit_activity'
    path('activities/', include('activities.urls')), 

    # 5. Mentors App URLs
    path('mentors/', include('mentors.urls')),

    # 6. API ENDPOINTS (Separate prefixes for clarity)
    path('api/fellows/', include('fellows.urls')),
    path('api/activities/', include('activities.urls')),

]

# --- Static and Media Files ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)