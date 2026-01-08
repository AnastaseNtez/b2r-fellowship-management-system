import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q, Avg, Case, When, Value, IntegerField
from django.http import HttpResponse
from django.contrib import messages

# DRF Imports
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

# Models, Forms, and Serializers
from .models import TrainingActivity
from .forms import ActivityReportForm
from .serializers import TrainingActivitySerializer
from .permissions import IsOwnerOrMentor
from locations.models import Sector, Village 
from fellows.models import Fellow 
from locations.models import District  

# --- 1. HELPER: MENTOR/COORDINATOR CHECK ---

def is_mentor(user):
    """
    Gatekeeper: Returns True if the user is an Admin, Mentor, or Coordinator.
    """
    if not user.is_authenticated:
        return False
        
    # 1. Check for Django Admin (is_staff/is_superuser)
    if user.is_staff or user.is_superuser:
        return True
        
    # 2. Check for Mentor profile
    if hasattr(user, 'mentor'):
        return True
        
    # 3. Check for Coordinator role in UserProfile
    if hasattr(user, 'userprofile') and user.userprofile.role in ['ADMIN', 'COORDINATOR']:
        return True
        
    return False

# --- 2. FELLOW WEB VIEWS (HTML) ---

@login_required
def fellow_dashboard_view(request):
    """HTML Dashboard for the logged-in Fellow."""
    fellow_profile, created = Fellow.objects.get_or_create(
        user=request.user,
        defaults={'status': 'ACTIVE'}
    )

    activities = TrainingActivity.objects.filter(fellow=fellow_profile).annotate(
        status_priority=Case(
            When(status='REVISION', then=Value(1)),
            When(status='PENDING', then=Value(2)),
            When(status='APPROVED', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('status_priority', '-date')

    context = {
        'total_trained': activities.filter(status='APPROVED').aggregate(
            Sum('number_of_farmers_trained')
        )['number_of_farmers_trained__sum'] or 0,
        'recent_activities': activities[:10],
        'fellow': fellow_profile
    }
    return render(request, 'activities/fellow_dashboard.html', context)

@login_required
def submit_activity_view(request):
    """Handles submission of new training logs via Web Form."""
    fellow_profile = get_object_or_404(Fellow, user=request.user)

    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES)
        if 'sector' in form.errors:
            del form.errors['sector']

        if form.is_valid():
            activity = form.save(commit=False)
            activity.fellow = fellow_profile
            activity.sector = fellow_profile.assigned_sector
            
            if activity.sector:
                activity.save()
                messages.success(request, "Training activity submitted successfully!")
                return redirect('all_activities')
            else:
                messages.error(request, "Your account has no assigned sector. Contact an Admin.")
    else:
        form = ActivityReportForm()
        
    return render(request, 'activities/submit_activity.html', {'form': form})

@login_required
def edit_report_view(request, pk):
    """Allows Fellows to edit reports, specifically those marked for REVISION."""
    report = get_object_or_404(TrainingActivity, pk=pk, fellow__user=request.user)
    fellow_profile = get_object_or_404(Fellow, user=request.user)
    
    if request.method == 'POST':
        form = ActivityReportForm(request.POST, request.FILES, instance=report)
        if 'sector' in form.errors:
            del form.errors['sector']
            
        if form.is_valid():
            updated_report = form.save(commit=False)
            updated_report.sector = fellow_profile.assigned_sector
            
            if updated_report.status == 'REVISION':
                updated_report.status = 'PENDING'
                updated_report.is_resubmitted = True
            
            updated_report.save()
            messages.success(request, "Report updated and resubmitted!")
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
    """Tabular list of all activities for the logged-in Fellow."""
    activities = TrainingActivity.objects.filter(fellow__user=request.user).order_by('-date')
    return render(request, 'activities/all_activities.html', {'activities': activities})

@login_required
def activity_detail_view(request, pk):
    """HTML view to display details for a single training activity."""
    if is_mentor(request.user):
        activity = get_object_or_404(TrainingActivity, pk=pk)
    else:
        activity = get_object_or_404(TrainingActivity, pk=pk, fellow__user=request.user)
        
    return render(request, 'activities/activity_detail.html', {'activity': activity})


# --- 3. MENTOR/COORDINATOR WEB VIEWS (HTML) ---

@login_required
@user_passes_test(is_mentor)
def mentor_dashboard_view(request):
    """Review dashboard for Mentors to see PENDING logs."""
    pending_reports = TrainingActivity.objects.filter(status='PENDING').order_by('-date')
    return render(request, 'activities/mentor_dashboard.html', {
        'pending_reports': pending_reports,
        'total_pending': pending_reports.count(),
    })

@login_required
@user_passes_test(is_mentor)
def review_report_view(request, pk):
    activity = get_object_or_404(TrainingActivity, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        # Mentor can correct the typo here before saving
        clean_village = request.POST.get('verified_village')

        activity.status = new_status
        activity.mentor_comments = request.POST.get('mentor_comments')

        if new_status == 'APPROVED':
            # 1. Save the mentor's confirmed version
            activity.verified_village = clean_village or activity.village_name
            # 2. Assign the CURRENT mentor who is logged in
            activity.approved_by = request.user
            # 3. Save any specific success story summary
            activity.success_stories = request.POST.get('success_stories')
        else:
            # If rejected/revision, clear approval metadata so it doesn't show in CSV
            activity.approved_by = None
            
        activity.save()
        return redirect('mentor_dashboard')
    
    return render(request, 'activities/review_report.html', {'report': activity})


# --- 4. ANALYTICS & CSV EXPORT ---

@login_required
@user_passes_test(is_mentor)
def export_activities_csv(request):
    # 1. Start with all activities and optimize for performance
    # select_related('approved_by') pulls the User object who reviewed the report
    activities = TrainingActivity.objects.all().select_related(
        'fellow__user', 
        'sector__district__province',
        'approved_by'
    )

    # 2. CAPTURE ACTIVE FILTERS (Matches Impact Summary View)
    search_query = request.GET.get('search')
    district_id = request.GET.get('district')

    if search_query:
        activities = activities.filter(training_topic__icontains=search_query)
    
    if district_id:
        activities = activities.filter(sector__district_id=district_id)

    # 3. Apply Final Ordering
    activities = activities.order_by('-date')
    
    # 4. Create CSV Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="b2r_filtered_impact_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Fellow Name', 'Date', 'Topic', 'Province', 'District', 'Sector', 
        'Village', 'Farmers Trained', 'Duration', 'Status', 
        'Approved By (Name)', 'Approved By (Email)', 
        'Challenges', 'Success Stories', 'Mentor Comments'
    ])
    
    for activity in activities:
        # Resolve village name based on approval status
        village_display = activity.verified_village if activity.status == 'APPROVED' and activity.verified_village else activity.village_name
        
        # Pull Mentor Details correctly
        
        mentor_name = activity.approved_by.get_full_name() if activity.approved_by else "Pending"
        mentor_email = activity.approved_by.email if activity.approved_by else "N/A"

        writer.writerow([
            activity.fellow.user.get_full_name(),
            activity.date,
            activity.training_topic,
            activity.sector.district.province.name if activity.sector.district.province else "N/A",
            activity.sector.district.name,
            activity.sector.name,
            village_display,
            activity.number_of_farmers_trained,
            activity.duration,
            activity.get_status_display(),
            mentor_name,
            mentor_email,
            activity.challenges_notes or "",
            activity.success_stories or "",
            activity.mentor_comments or ""
        ])
        
    return response

@login_required
def impact_summary(request):
    """HTML page showing filtered high-level program statistics."""
    approved_data = TrainingActivity.objects.filter(status='APPROVED')

    search_query = request.GET.get('search')
    district_id = request.GET.get('district')

    if search_query:
        approved_data = approved_data.filter(training_topic__icontains=search_query)

    if district_id:
        approved_data = approved_data.filter(sector__district_id=district_id)

    total_stats = approved_data.aggregate(
        total_farmers=Sum('number_of_farmers_trained'),
        total_sessions=Count('id'),
        avg_reach=Avg('number_of_farmers_trained')
    )

    topic_data = approved_data.values('training_topic').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    context = {
        'total_farmers': total_stats['total_farmers'] or 0,
        'total_sessions': total_stats['total_sessions'] or 0,
        'avg_reach': round(total_stats['avg_reach'] or 0, 1),
        'geographic_data': approved_data.values('sector__district__name').annotate(
            farmers=Sum('number_of_farmers_trained'),
            sessions=Count('id')
        ).order_by('-farmers'),
        'topic_data': topic_data,
        'districts': District.objects.all().order_by('name'),
    }
    return render(request, 'activities/impact_summary.html', context)


# --- 5. REST API VIEWS (JSON) ---

class TrainingActivityViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or hasattr(user, 'mentor'):
            return TrainingActivity.objects.all().select_related(
                'fellow__user', 'sector__district'
            ).order_by('-date')
        return TrainingActivity.objects.filter(fellow__user=user)

    def perform_create(self, serializer):
        # Checks for either fellow or fellow_profile depending on the model setup
        if hasattr(self.request.user, 'fellow'):
            serializer.save(fellow=self.request.user.fellow)
        elif hasattr(self.request.user, 'fellow_profile'):
            serializer.save(fellow=self.request.user.fellow_profile)
        else:
            serializer.save()

class ImpactReportDataAPIView(APIView):
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = TrainingActivity.objects.aggregate(
            pending=Count('id', filter=Q(status='PENDING')),
            total_farmers=Sum('number_of_farmers_trained', filter=Q(status='APPROVED')) or 0
        )
        return Response(stats)

class FellowPerformanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        performance_data = TrainingActivity.objects.filter(status='APPROVED').values(
            'fellow__user__first_name', 
            'fellow__user__last_name',
            'fellow__assigned_sector__name' 
        ).annotate(
            total_impact=Sum('number_of_farmers_trained'),
            session_count=Count('id')
        ).order_by('-total_impact')

        return Response({"leaderboard": list(performance_data)})