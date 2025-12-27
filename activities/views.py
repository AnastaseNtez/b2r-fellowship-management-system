from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
import csv
from django.http import HttpResponse

from .forms import ActivityReportForm
from .models import TrainingActivity
from .serializers import TrainingActivitySerializer 
from .utils import get_program_metrics
from fellows.models import Fellow 

# --- FELLOW WEB VIEWS ---

@login_required
def submit_activity_view(request):
    """Allows Fellows to submit new training reports."""
    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            profile = request.user.fellow_profile
            activity.fellow = profile
            activity.sector = profile.assigned_sector
            activity.save()
            messages.success(request, "Activity report submitted successfully!")
            return redirect('dashboard')
    else:
        form = ActivityReportForm()
    return render(request, 'activities/submit_report.html', {'form': form, 'edit_mode': False})

@login_required
def edit_report_view(request, pk):
    """Allows Fellows to see mentor feedback and update their report."""
    # Ensure the fellow can only edit their own reports that are marked for REVISION
    report = get_object_or_404(TrainingActivity, pk=pk, fellow=request.user.fellow_profile)
    
    if report.status != 'REVISION':
        messages.error(request, "This report cannot be edited at this time.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.status = 'PENDING'
            activity.is_resubmitted = True
            # Optional: Clear comments so the mentor sees a fresh resubmission
            # activity.mentor_comments = "" 
            activity.save()
            messages.success(request, "Report resubmitted for review!")
            return redirect('dashboard')
    else:
        form = ActivityReportForm(instance=report)
    
    # Passing 'report' here allows submit_report.html to show report.mentor_comments
    return render(request, 'activities/submit_report.html', {
        'form': form,
        'edit_mode': True,
        'report': report
    })

@login_required
def all_activities_view(request):
    """Displays every report submitted by the fellow."""
    try:
        fellow = request.user.fellow_profile
    except AttributeError:
        messages.error(request, "Fellow profile not found.")
        return redirect('login')

    activities = TrainingActivity.objects.filter(fellow=fellow).order_by('-date')
    
    return render(request, 'activities/all_activities.html', {
        'activities': activities
    })

# --- MENTOR WEB VIEWS ---

@login_required
def mentor_dashboard_view(request):
    """Portal for Mentors."""
    # Role check to prevent Fellows from accessing Mentor data
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'MENTOR':
        return redirect('dashboard')
    
    # Use order_by, NOT order_of
    pending_reports = TrainingActivity.objects.filter(
        fellow__mentor__user=request.user, # Adjust based on your Mentor model relation
        status='PENDING'
    ).order_by('-date')
    
    return render(request, 'activities/mentor_dashboard.html', {
        'pending_reports': pending_reports,
        'total_pending': pending_reports.count()
    })

@login_required
def review_report_view(request, pk):
    """Detailed view for Mentors to approve or reject reports with feedback."""
    report = get_object_or_404(TrainingActivity, pk=pk)
    
    if not hasattr(request.user, 'mentor_profile') or request.user.mentor_profile != report.fellow.mentor:
        messages.error(request, "You are not authorized to review this report.")
        return redirect('mentor_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('mentor_comments') 
        
        report.mentor_comments = feedback

        if action == 'approve':
            report.status = 'APPROVED'
            report.is_resubmitted = False
            messages.success(request, "Report approved.")
        elif action == 'reject':
            report.status = 'REVISION'
            report.is_resubmitted = False
            messages.warning(request, "Report sent back for revision with feedback.")
        
        report.save()
        return redirect('mentor_dashboard')

    return render(request, 'activities/review_report.html', {'report': report})

@login_required
def approve_report(request, pk):
    """Quick approval endpoint."""
    if not hasattr(request.user, 'mentor_profile'):
        return redirect('dashboard')
        
    report = get_object_or_404(TrainingActivity, pk=pk)
    
    if report.fellow.mentor != request.user.mentor_profile:
        messages.error(request, "Unauthorized.")
        return redirect('mentor_dashboard')

    report.status = 'APPROVED'
    report.is_resubmitted = False
    report.save()
    messages.success(request, "Activity approved successfully.")
    return redirect('mentor_dashboard')

# --- REST API & EXPORTS ---

class TrainingActivityViewSet(viewsets.ModelViewSet):
    """API endpoint with role-based data filtering."""
    serializer_class = TrainingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TrainingActivity.objects.all()
        if hasattr(user, 'mentor_profile'):
            return TrainingActivity.objects.filter(fellow__mentor=user.mentor_profile)
        if hasattr(user, 'fellow_profile'):
            return TrainingActivity.objects.filter(fellow=user.fellow_profile)
        return TrainingActivity.objects.filter(status='APPROVED')

    def perform_create(self, serializer):
        serializer.save(fellow=self.request.user.fellow_profile)

class DashboardStatsAPIView(APIView):
    """Returns high-level impact metrics."""
    def get(self, request):
        metrics = get_program_metrics()
        return Response(metrics)

def export_activities_csv(request):
    """Generates a CSV of approved reports."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="b2r_training_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Fellow', 'District', 'Sector', 'Topic', 'Farmers Trained'])

    activities = TrainingActivity.objects.filter(status='APPROVED').select_related('fellow', 'sector__district')
    for act in activities:
        writer.writerow([
            act.date, 
            act.fellow.user.get_full_name(), 
            act.sector.district.name,
            act.sector.name,
            act.training_topic,
            act.number_of_farmers_trained
        ])
    return response