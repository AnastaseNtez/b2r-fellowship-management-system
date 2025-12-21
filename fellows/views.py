from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string 
from django.contrib.auth.decorators import login_required

from .forms import FellowRegistrationForm
from accounts.models import UserProfile 
from .models import Fellow 
from activities.models import TrainingActivity

User = get_user_model()

def fellow_register_view(request):
    """
    Handles the registration of a new Fellow via a web form.
    It atomically creates a Django User, a UserProfile (Role: Fellow), and the Fellow record.
    """
    if request.method == 'POST':
        form = FellowRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Extracting data for User creation
                    email = form.cleaned_data.pop('email')
                    first_name = form.cleaned_data.pop('first_name')
                    last_name = form.cleaned_data.pop('last_name')
                    
                    # Clean up location fields used for filtering in the form
                    form.cleaned_data.pop('province', None)
                    form.cleaned_data.pop('district', None)
                    
                    # Generate temporary password
                    raw_password = get_random_string(length=12) 
                    
                    user = User.objects.create_user(
                        username=email, 
                        email=email,
                        password=raw_password, 
                        first_name=first_name, 
                        last_name=last_name,
                        is_active=True
                    )

                    # Create the UserProfile gatekeeper
                    UserProfile.objects.create(
                        user=user,
                        role=UserProfile.Role.FELLOW 
                    )
                    
                    # Link the Fellow data
                    fellow = form.save(commit=False)
                    fellow.user = user 
                    fellow.save()
                    
                    messages.success(request, 
                        f"Fellow {fellow.get_full_name} registered successfully. "
                        f"Temporary Password: {raw_password}"
                    )
                    return redirect('/admin/') 

            except Exception as e:
                messages.error(request, f"Error during registration: {e}")
    else:
        form = FellowRegistrationForm()

    return render(request, 'fellows/fellow_form.html', {'form': form})

@login_required
def dashboard_view(request):
    """
    Landing page for logged-in Fellows.
    Now includes Mentor information and recent activities.
    """
    # Fetch the Fellow profile linked to the user
    fellow = getattr(request.user, 'fellow_profile', None) 
    
    recent_activities = []
    mentor = None
    
    if fellow:
        # Fetch activities for the activity log
        recent_activities = TrainingActivity.objects.filter(fellow=fellow).order_by('-date')[:5]
        # Get the assigned mentor for display
        mentor = fellow.mentor
    
    return render(request, 'fellows/dashboard.html', {
        'fellow': fellow,
        'user': request.user,
        'mentor': mentor, # New: allow the Fellow to see who their mentor is
        'activities': recent_activities
    })