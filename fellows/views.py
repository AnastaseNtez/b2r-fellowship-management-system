from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField

# Import models
from .models import Fellow
from activities.models import TrainingActivity

def fellow_register_view(request):
    """Handles fellow registration logic."""
    return render(request, 'fellows/register.html')

@login_required
def dashboard_view(request):
    """
    Fellow dashboard with role-checking to prevent login loops.
    """
    # 1. First, check if the user is actually a Mentor
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'MENTOR':
        return redirect('mentor_dashboard')

    # 2. Try to get the Fellow profile
    try:
        fellow = request.user.fellow_profile
    except AttributeError:
        # If they aren't a mentor and have no fellow profile, 
        # only THEN redirect or show an error.
        if request.user.is_staff:
            return redirect('/admin/')
        messages.error(request, "Fellow profile not found.")
        # Redirect to a neutral page or logout to break the loop
        return redirect('login') 

    # 3. Priority ordering logic for Fellows
    priority_order = Case(
        When(status='REVISION', then=Value(1)),
        When(status='PENDING', then=Value(2)),
        When(status='APPROVED', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )

    activities_queryset = TrainingActivity.objects.filter(fellow=fellow).annotate(
        priority=priority_order
    ).order_by('priority', '-date')

    stats = {
        'to_fix': activities_queryset.filter(status='REVISION').count(),
        'pending': activities_queryset.filter(status='PENDING').count(),
        'approved': activities_queryset.filter(status='APPROVED').count(),
    }

    return render(request, 'fellows/dashboard.html', {
        'recent_activities': activities_queryset[:10],
        'stats': stats,
        'fellow': fellow
    })

@login_required
def fellow_profile_view(request):
    """Displays the profile of the fellow."""
    fellow = get_object_or_404(Fellow, user=request.user)
    return render(request, 'fellows/profile.html', {'fellow': fellow})