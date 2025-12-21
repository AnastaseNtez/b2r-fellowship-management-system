from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib import messages 

""" Scirpt that handles where users go after they log in"""

@login_required
def smart_redirect(request):
    """
    Traffic controller: Checks the user's role and sends them 
    to the appropriate dashboard.
    """
    try:
        # Access the UserProfile linked to the logged-in user
        profile = request.user.userprofile
        
        if profile.role == 'MENTOR':
            return redirect('mentor_dashboard')
        elif profile.role == 'FELLOW':
            return redirect('dashboard')
            
    except UserProfile.DoesNotExist:
        # If it's a superuser/admin without a profile, send to Django Admin
        if request.user.is_staff:
            return redirect('/admin/')
            
    # Default fallback if something is wrong
    messages.error(request, "User profile not found. Please contact the administrator.")
    return redirect('login')