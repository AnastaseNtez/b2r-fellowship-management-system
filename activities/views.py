import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q, Avg
from django.http import HttpResponse

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import messages

# Models & Forms
from .models import TrainingActivity
from .forms import ActivityReportForm
from .serializers import TrainingActivitySerializer
from .permissions import IsOwnerOrMentor  # Custom RBAC logic
from fellows.models import Fellow 

# --- 1. HELPER: MENTOR/COORDINATOR CHECK ---
def is_mentor(user):
    """Checks if the user has mentor/coordinator status or is staff/superuser."""
    return user.is_authenticated and (
        user.is_staff or 
        user.is_superuser or 
        hasattr(user, 'mentor') or
        (hasattr(user, 'userprofile') and user.userprofile.role in ['ADMIN', 'COORDINATOR'])
    )

# --- 2. FELLOW WEB VIEWS ---

@login_required
def fellow_dashboard_view(request):
    # This automatically creates the missing record if it doesn't exist
    fellow_profile, created = Fellow.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'email': request.user.email
        }
    )

    activities = TrainingActivity.objects.filter(fellow=fellow_profile)
    
    context = {
        'total_trained': activities.aggregate(Sum('number_of_farmers_trained'))['number_of_farmers_trained__sum'] or 0,
        'recent_activities': activities.order_by('-date')[:5],
    }
    return render(request, 'activities/fellow_dashboard.html', context)

@login_required
def submit_activity_view(request):
    """Allows Fellows to log daily training sessions."""
    try:
        fellow_profile = Fellow.objects.get(user=request.user)
    except Fellow.DoesNotExist:
        return HttpResponse(
            f"Access Denied: No Fellow record found for {request.user.email}.", 
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
    """Allows Fellows to update a report (e.g., if revision is requested)."""
    report = get_object_or_404(TrainingActivity, pk=pk, fellow__user=request.user)
    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
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
        'report': report 
    })

@login_required
def all_activities_view(request):
    """Web view for Fellows to see their own activity history."""
    activities = TrainingActivity.objects.filter(fellow__user=request.user).order_by('-date')
    return render(request, 'activities/all_activities.html', {'activities': activities})

# --- 3. MENTOR/COORDINATOR WEB VIEWS ---

@login_required
@user_passes_test(is_mentor)
def mentor_dashboard_view(request):
    """Dashboard for Mentors to review pending submissions."""
    pending_reports = TrainingActivity.objects.filter(status='PENDING').order_by('-date')
    return render(request, 'activities/mentor_dashboard.html', {
        'pending_reports': pending_reports,
        'total_pending': pending_reports.count(),
    })

@login_required
@user_passes_test(is_mentor)
def review_report_view(request, pk):
    """Mentors can Approve or Request Revision on activities."""
    report = get_object_or_404(TrainingActivity, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
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
    """Exports all activity data to CSV for donor/admin reporting."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="b2r_impact_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Fellow', 'Date', 'Topic', 'District', 'Farmers Trained', 'Status'])
    
    for activity in TrainingActivity.objects.all().select_related('fellow__user', 'sector__district'):
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
    """Web view aggregating program-wide reach for the Impact Dashboard."""
    approved_data = TrainingActivity.objects.filter(status='APPROVED')

    total_stats = approved_data.aggregate(
        total_farmers=Sum('number_of_farmers_trained'),
        total_sessions=Count('id')
    )

    total_farmers = total_stats['total_farmers'] or 0
    total_sessions = total_stats['total_sessions'] or 0
    avg_reach = round(total_farmers / total_sessions, 1) if total_sessions > 0 else 0

    geographic_data = approved_data.values('sector__district__name') \
        .annotate(
            sessions=Count('id'),
            farmers=Sum('number_of_farmers_trained')
        ).order_by('-farmers')

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

# --- 5. REST API (JWT Authenticated) ---

class TrainingActivityViewSet(viewsets.ModelViewSet):
    """
    API Viewset for Training Logs.
    - Mentors/Admins/Viewers see all logs.
    - Fellows only see their own logs.
    """
    serializer_class = TrainingActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMentor]

    def get_queryset(self):
        user = self.request.user
        # Logic to return full dataset for staff, mentors, or read-only viewers
        if user.is_staff or user.is_superuser or hasattr(user, 'mentor') or \
           (hasattr(user, 'userprofile') and user.userprofile.role in ['ADMIN', 'COORDINATOR', 'VIEWER']):
            return TrainingActivity.objects.all()
        return TrainingActivity.objects.filter(fellow__user=user)

    def perform_create(self, serializer):
        # Automatically link the activity to the fellow profile of the current user
        serializer.save(fellow=self.request.user.fellow)

class ImpactReportDataAPIView(APIView):
    """Returns aggregated data by district for frontend visualizations."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        data = TrainingActivity.objects.filter(status='APPROVED').values(
            'sector__district__name'
        ).annotate(
            sessions=Count('id'),
            farmers=Sum('number_of_farmers_trained')
        ).order_by('-farmers')
        return Response({'by_district': list(data)})

class DashboardStatsAPIView(APIView):
    """Returns summary counts for dashboard statistic cards."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = TrainingActivity.objects.aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            total_farmers=Sum('number_of_farmers_trained', filter=Q(status='APPROVED')) or 0
        )
        return Response(stats)

class FellowPerformanceAPIView(APIView):
    """
    Returns an enhanced leaderboard of Fellows including:
    - Total farmers reached
    - Number of approved training sessions
    - Average farmers per session
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Optimized query with multiple annotations
        performance_data = TrainingActivity.objects.filter(status='APPROVED').values(
            'fellow__user__first_name', 
            'fellow__user__last_name',
            'fellow__assigned_sector' # Adding location context
        ).annotate(
            total_impact=Sum('number_of_farmers_trained'),
            session_count=Count('id'),
            avg_per_session=Avg('number_of_farmers_trained')
        ).order_by('-total_impact')

        # Formatting the response for better readability
        leaderboard = []
        for entry in performance_data:
            leaderboard.append({
                "name": f"{entry['fellow__user__first_name']} {entry['fellow__user__last_name']}",
                "sector": entry['fellow__assigned_sector'],
                "metrics": {
                    "total_farmers_trained": entry['total_impact'],
                    "sessions_completed": entry['session_count'],
                    "avg_farmers_per_session": round(entry['avg_per_session'], 1)
                }
            })

        return Response({
            "count": len(leaderboard),
            "leaderboard": leaderboard
        })