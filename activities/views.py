from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, permissions

from .forms import ActivityReportForm
from .models import TrainingActivity
from .serializers import TrainingActivitySerializer 

from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_program_metrics

import csv
from django.http import HttpResponse

# --- STANDARD WEB VIEWS ---

@login_required
def submit_activity_view(request):
    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES) # Added request.FILES for photos
        if form.is_valid():
            activity = form.save(commit=False)
            activity.fellow = request.user.fellow_profile 
            activity.save()
            
            messages.success(request, "Activity report submitted successfully!")
            return redirect('dashboard')
    else:
        form = ActivityReportForm()
    
    return render(request, 'activities/submit_report.html', {'form': form})

@login_required
def review_report_view(request, pk):
    report = get_object_or_404(TrainingActivity, pk=pk)
    
    # Security: Ensure only the assigned mentor can review
    if not hasattr(request.user, 'mentor_profile') or request.user.mentor_profile != report.fellow.mentor:
        messages.error(request, "You are not authorized to review this report.")
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            report.status = TrainingActivity.Status.APPROVED
            messages.success(request, f"Report approved.")
        elif action == 'reject':
            report.status = TrainingActivity.Status.REVISION
            messages.warning(request, f"Report sent back for revision.")
        
        report.save()
        return redirect('dashboard') # Adjust to mentor dashboard name

    return render(request, 'activities/review_report.html', {'report': report})


# --- REST API VIEWSETS ---

class TrainingActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows activities to be viewed or edited.
    Implements role-based data filtering.
    """
    serializer_class = TrainingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # 1. Admins see everything
        if user.is_staff:
            return TrainingActivity.objects.all()
        
        # 2. Coordinators see logs for Fellows assigned to them
        if hasattr(user, 'mentor_profile'):
            return TrainingActivity.objects.filter(fellow__mentor=user.mentor_profile)
        
        # 3. Fellows see only their own logs
        if hasattr(user, 'fellow_profile'):
            return TrainingActivity.objects.filter(fellow=user.fellow_profile)
            
        # 4. Viewers (Donors) see only approved logs
        return TrainingActivity.objects.filter(status='APPROVED')

    def perform_create(self, serializer):
        # Automatically assign the logged-in Fellow to the report
        serializer.save(fellow=self.request.user.fellow_profile)

# Analytics API endpoint
class DashboardStatsAPIView(APIView):
    """
    Returns high-level impact metrics for Admins and Viewers (Donors).
    """
    def get(self, request):
        # Optional: Add permission check here (e.g., only Admin/Viewer)
        metrics = get_program_metrics()
        return Response(metrics)
    
# CSV export for donors
def export_activities_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="b2r_training_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Fellow', 'Province', 'District', 'Sector', 'Topic', 'Farmers Trained'])

    activities = TrainingActivity.objects.filter(status='APPROVED').select_related('fellow', 'sector__district__province')
    
    for act in activities:
        writer.writerow([
            act.date, 
            act.fellow.user.get_full_name(), 
            act.sector.district.province.name,
            act.sector.district.name,
            act.sector.name,
            act.training_topic,
            act.number_of_farmers_trained
        ])

    return response