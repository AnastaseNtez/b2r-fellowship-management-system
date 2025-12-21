from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from activities.models import TrainingActivity
from .forms import MentorRegistrationForm
from .models import Mentor

def mentor_register_view(request):
    """Handles Atomic creation of Mentor, User, and Profile."""
    if request.method == 'POST':
        form = MentorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    email = form.cleaned_data.pop('email')
                    first_name = form.cleaned_data.pop('first_name')
                    last_name = form.cleaned_data.pop('last_name')
                    
                    temp_password = get_random_string(12)
                    user = User.objects.create_user(
                        username=email, email=email, password=temp_password,
                        first_name=first_name, last_name=last_name
                    )

                    UserProfile.objects.create(user=user, role='MENTOR')

                    mentor = form.save(commit=False)
                    mentor.user = user
                    mentor.save()

                    messages.success(request, f"Mentor {first_name} registered. Temp Password: {temp_password}")
                    return redirect('/admin/')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = MentorRegistrationForm()
    return render(request, 'mentors/register.html', {'form': form})

@login_required
def mentor_dashboard(request):
    """Displays pending tasks and history for the logged-in Mentor."""
    mentor = getattr(request.user, 'mentor_profile', None)
    
    if not mentor:
        messages.error(request, "Access denied. Mentor profile not found.")
        return redirect('login')

    # Filter reports by Fellows assigned to THIS mentor
    pending_reports = TrainingActivity.objects.filter(
        fellow__mentor=mentor, 
        status='PENDING'
    ).order_by('-date')
    
    recent_history = TrainingActivity.objects.filter(
        fellow__mentor=mentor
    ).exclude(status='PENDING').order_by('-updated_at')[:10]

    return render(request, 'mentors/dashboard.html', {
        'mentor': mentor,
        'pending_reports': pending_reports,
        'recent_history': recent_history
    })

@login_required
def review_activity(request, pk):
    """Allows a Mentor to Approve or request Revision on a Fellow's report."""
    mentor = getattr(request.user, 'mentor_profile', None)
    report = get_object_or_404(TrainingActivity, pk=pk, fellow__mentor=mentor)

    if request.method == 'POST':
        status = request.POST.get('status')
        comments = request.POST.get('mentor_comments')
        
        if status in ['APPROVED', 'REVISION']:
            report.status = status
            report.mentor_comments = comments
            report.save()
            messages.success(request, f"Report for {report.fellow.get_full_name} has been {status.lower()}.")
            return redirect('mentor_dashboard')

    return render(request, 'mentors/review_report.html', {'report': report})