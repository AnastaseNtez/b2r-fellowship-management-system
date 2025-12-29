from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Count 
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Import models and serializers
from .models import Fellow
from .serializers import FellowSerializer
from activities.models import TrainingActivity
from activities.serializers import TrainingActivitySerializer

# --- WEB VIEWS ---

def fellow_register_view(request):
    """Handles fellow registration logic for the web browser."""
    return render(request, 'fellows/register.html')

@login_required
def dashboard_view(request):
    """Fellow web dashboard with activity list and stats."""
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'MENTOR':
        return redirect('mentor_dashboard')

    try:
        fellow = request.user.fellow_profile
    except AttributeError:
        if request.user.is_staff:
            return redirect('/admin/')
        messages.error(request, "Fellow profile not found.")
        return redirect('login') 

    # Order activities by priority status for the dashboard
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

# --- API VIEWSET ---

class FellowViewSet(viewsets.ModelViewSet):
    """API ViewSet for Fellow management (JSON)."""
    queryset = Fellow.objects.all()
    serializer_class = FellowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        GET /api/fellows/statistics/
        Breakdown of fellow counts by status and geography.
        """
        queryset = self.get_queryset()
        
        # 1. Initialize all possible statuses with 0 using the Status nested class
        status_breakdown = {choice[0]: 0 for choice in Fellow.Status.choices}
        
        # 2. Update with actual counts from the database
        status_counts = queryset.values('status').annotate(total=Count('id'))
        for item in status_counts:
            status_breakdown[item['status']] = item['total']

        # 3. Aggregate counts for geographic distribution
        district_counts = queryset.values('assigned_sector__district__name').annotate(total=Count('id'))

        stats = {
            'program_overview': {
                'total_fellows': queryset.count(),
                'status_breakdown': status_breakdown
            },
            'geographic_distribution': {
                item['assigned_sector__district__name'] or 'Unassigned': item['total'] 
                for item in district_counts
            }
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """GET /api/fellows/{id}/activities/"""
        fellow = self.get_object()
        activities = TrainingActivity.objects.filter(fellow=fellow)
        serializer = TrainingActivitySerializer(activities, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Assign the user when creating via API."""
        serializer.save(user=self.request.user)