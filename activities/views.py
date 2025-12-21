from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ActivityReportForm
from .models import TrainingActivity

@login_required
def submit_activity_view(request):
    if request.method == 'POST':
        form = ActivityReportForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            # Link the activity to the logged-in Fellow's profile
            activity.fellow = request.user.fellow_profile 
            activity.save()
            
            messages.success(request, "Activity report submitted successfully!")
            return redirect('dashboard')
    else:
        form = ActivityReportForm()
    
    return render(request, 'activities/submit_report.html', {'form': form})

@login_required
def review_report_view(request, pk):
    # Ensure only the assigned mentor can review this report
    report = get_object_or_404(TrainingActivity, pk=pk)
    
    # Security Check: Is the logged-in user the mentor for this fellow?
    if request.user.mentor_profile != report.fellow.mentor:
        messages.error(request, "You are not authorized to review this report.")
        return redirect('mentor_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            report.status = 'Approved'
            messages.success(request, f"Report for {report.fellow.user.get_full_name()} approved.")
        elif action == 'reject':
            report.status = 'Rejected'
            messages.error(request, f"Report for {report.fellow.user.get_full_name()} rejected.")
        
        report.save()
        return redirect('mentor_dashboard')

    return render(request, 'activities/review_report.html', {'report': report})