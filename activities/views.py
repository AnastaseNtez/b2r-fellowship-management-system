from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

# Models & Forms
from .models import TrainingActivity
from .forms import ActivityReportForm
from .serializers import TrainingActivitySerializer
from .permissions import IsOwnerOrMentor
from fellows.models import Fellow  # Ensure this import exists

# --- 1. HELPER: MENTOR CHECK ---
def is_mentor(user):
    """Checks if the user has mentor status or is staff/superuser."""
    return user.is_authenticated and (
        user.is_staff or 
        user.is_superuser or 
        hasattr(user, 'mentor')
    )

# --- 2. FELLOW WEB VIEWS ---

@login_required
def submit_activity_view(request):
    # Try to find the Fellow profile by querying the model directly
    try:
        fellow_profile = Fellow.objects.get(user=request.user)
    except Fellow.DoesNotExist:
        return HttpResponse(
            f"Debug Info: Logged in as {request.user.email}. "
            f"No Fellow record found linked to this specific User ID.", 
            status=403
        )

    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.fellow = fellow_profile 
            activity.sector = fellow_profile.assigned_sector
            activity.save()
            return redirect('all_activities')
    else:
        form = ActivityReportForm()
        
    return render(request, 'activities/submit_activity.html', {'form': form})

@login_required
def edit_report_view(request, pk):
    """Allows Fellows to update a report, especially if marked for REVISION."""
    report = get_object_or_404(TrainingActivity, pk=pk, fellow__user=request.user)
    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            # If it was in REVISION, move it back to PENDING for re-review
            if report.status == 'REVISION':
                report.status = 'PENDING'
                report.is_resubmitted = True
            form.save()
            return redirect('all_activities')
    else:
        form = ActivityReportForm(instance=report)
    return render(request, 'activities/submit_activity.html', {
        'form': form, 
        'edit_mode': True,
        'report': report # Passing report so we can show Mentor comments in the template
    })

@login_required
def all_activities_view(request):
    """Corrected order_by syntax"""
    activities = TrainingActivity.objects.filter(fellow__user=request.user).order_by('-date')
    return render(request, 'activities/all_activities.html', {'activities': activities})

# --- 3. MENTOR WEB VIEWS ---

@login_required
@user_passes_test(is_mentor)
def mentor_dashboard_view(request):
    """Dashboard for Mentors to see pending items."""
    # This fetches all reports that need review
    pending_reports = TrainingActivity.objects.filter(status='PENDING').order_by('-date')
    
    return render(request, 'activities/mentor_dashboard.html', {
        'pending_reports': pending_reports,
        'total_pending': pending_reports.count(),
    })

@login_required
@user_passes_test(is_mentor)
def review_report_view(request, pk):
    """Standardized mentor_comments naming"""
    report = get_object_or_404(TrainingActivity, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        # Matches the 'name' attribute in your review_report.html textarea
        report.mentor_comments = request.POST.get('mentor_comments') 
        
        if action == 'approve':
            report.status = 'APPROVED'
        elif action == 'reject':
            report.status = 'REVISION'
            
        report.save()
        return redirect('mentor_dashboard')
    return render(request, 'activities/review_report.html', {'report': report})

# --- 4. ANALYTICS & EXPORT ---

@login_required
@user_passes_test(is_mentor)
def export_activities_csv(request):
    """Exports all activity data to CSV for reporting."""
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="b2r_impact_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Fellow', 'Date', 'Topic', 'District', 'Farmers Trained', 'Status'])
    
    for activity in TrainingActivity.objects.all():
        writer.writerow([
            activity.fellow.user.get_full_name(),
            activity.date,
            activity.training_topic,
            activity.sector.district.name,
            activity.number_of_farmers_trained,
            activity.status
        ])
    return response

@login_required
def impact_summary(request):
    """
    Aggregates fellowship data for the Impact Summary page.
    Only includes 'APPROVED' activities to ensure data integrity.
    """
    # 1. Filter for only approved logs
    approved_data = TrainingActivity.objects.filter(status='APPROVED')

    # 2. Top-level Stat Cards
    # Uses the correct field name from your error: 'number_of_farmers_trained'
    total_stats = approved_data.aggregate(
        total_farmers=Sum('number_of_farmers_trained'),
        total_sessions=Count('id')
    )

    total_farmers = total_stats['total_farmers'] or 0
    total_sessions = total_stats['total_sessions'] or 0
    
    # Calculate average (handle division by zero)
    avg_reach = round(total_farmers / total_sessions, 1) if total_sessions > 0 else 0

    # 3. Geographic Coverage Table
    # Aggregates reach by District (via the Sector relationship)
    geographic_data = approved_data.values('sector__district__name') \
        .annotate(
            sessions=Count('id'),
            farmers=Sum('number_of_farmers_trained')
        ).order_by('-farmers')

    # 4. Training Topic Reach (for the sidebar/chart)
    topic_data = approved_data.values('training_topic') \
        .annotate(total=Sum('number_of_farmers_trained')) \
        .order_by('-total')[:5]

    context = {
        'total_farmers': total_farmers,
        'total_sessions': total_sessions,
        'avg_reach': avg_reach,
        'geographic_data': geographic_data,
        'topic_data': topic_data,
    }

    return render(request, 'activities/impact_summary.html', context)

# --- 5. REST API (Used by JavaScript Dashboard) ---

class TrainingActivityViewSet(viewsets.ModelViewSet):
    """Standard API for Activity logs."""
    serializer_class = TrainingActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMentor]

    def get_queryset(self):
        if self.request.user.is_staff:
            return TrainingActivity.objects.all()
        return TrainingActivity.objects.filter(fellow__user=self.request.user)

class ImpactReportDataAPIView(APIView):
    """API providing data for the Leaderboard."""
    def get(self, request):
        data = TrainingActivity.objects.filter(status='APPROVED').values(
            'sector__district__name'
        ).annotate(
            sessions=Count('id'),
            farmers=Sum('number_of_farmers_trained')
        ).order_by('-farmers')
        return Response({'by_district': list(data)})

class DashboardStatsAPIView(APIView):
    """API providing summary stats (total farmers, pending count)."""
    def get(self, request):
        stats = TrainingActivity.objects.aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            total_farmers=Sum('number_of_farmers_trained', filter=Q(status='APPROVED')) or 0
        )
        return Response(stats)

class FellowPerformanceAPIView(APIView):
    """API for ranking individual Fellow impact."""
    def get(self, request):
        perf = TrainingActivity.objects.filter(status='APPROVED').values(
            'fellow__user__first_name', 'fellow__user__last_name'
        ).annotate(
            total_trained=Sum('number_of_farmers_trained')
        ).order_by('-total_trained')
        return Response(list(perf))