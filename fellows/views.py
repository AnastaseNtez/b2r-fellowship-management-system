from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Import models, serializers, and forms
from .models import Fellow
from .serializers import FellowSerializer
from .forms import FellowForm
from activities.models import TrainingActivity
from activities.serializers import TrainingActivitySerializer

# --- SECURITY UTILITIES ---

def is_admin_or_coordinator(user):
    """Checks if the user has administrative or coordinator privileges."""
    return user.is_staff or user.groups.filter(name='Coordinator').exists()


# --- FELLOW WEB VIEWS (For Fellows) ---

def fellow_register_view(request):
    """Handles fellow registration logic for the web browser."""
    return render(request, 'fellows/register.html')

@login_required
def dashboard_view(request):
    """Fellow web dashboard with activity list and stats."""
    # Redirect Mentors to their specific dashboard
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'MENTOR':
        return redirect('mentor_dashboard')

    try:
        fellow = request.user.fellow_profile
    except AttributeError:
        # If staff, take them to admin; otherwise, they need a profile
        if request.user.is_staff:
            return redirect('/admin/')
        messages.error(request, "Fellow profile not found.")
        return redirect('login') 

    # Order activities by priority status (Revision first, then Pending, then Approved)
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

    # Aggregate statistics for the dashboard cards
    stats = {
        'to_fix': activities_queryset.filter(status='REVISION').count(),
        'pending': activities_queryset.filter(status='PENDING').count(),
        'approved': activities_queryset.filter(status='APPROVED').count(),
        'total_trained': activities_queryset.filter(status='APPROVED').aggregate(
            total=Sum('number_of_farmers_trained'))['total'] or 0
    }

    return render(request, 'fellows/dashboard.html', {
        'recent_activities': activities_queryset[:10],
        'stats': stats,
        'fellow': fellow
    })


# --- ADMIN/COORDINATOR VIEWS (Fellow Management CRUD) ---

@user_passes_test(is_admin_or_coordinator)
def fellow_list_view(request):
    """READ: Displays a management table of all fellows."""
    fellows = Fellow.objects.all().order_by('-id')
    return render(request, 'fellows/fellow_list.html', {'fellows': fellows})

@user_passes_test(is_admin_or_coordinator)
def fellow_create_view(request):
    """CREATE: Handles creating a new fellow and their User account."""
    if request.method == 'POST':
        form = FellowForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New fellow created successfully!")
            return redirect('fellow_list')
    else:
        form = FellowForm()
    return render(request, 'fellows/fellow_form.html', {
        'form': form, 
        'title': 'Add New Fellow'
    })

@user_passes_test(is_admin_or_coordinator)
def fellow_edit_view(request, pk):
    """UPDATE: Handles editing an existing fellow profile."""
    fellow = get_object_or_404(Fellow, pk=pk)
    if request.method == 'POST':
        form = FellowForm(request.POST, instance=fellow)
        if form.is_valid():
            form.save()
            messages.success(request, f"Details for {fellow.user.get_full_name()} updated.")
            return redirect('fellow_list')
    else:
        form = FellowForm(instance=fellow)
    return render(request, 'fellows/fellow_form.html', {
        'form': form, 
        'title': 'Edit Fellow'
    })

@user_passes_test(is_admin_or_coordinator)
def fellow_delete_view(request, pk):
    """DELETE: Removes a fellow and their associated User account."""
    fellow = get_object_or_404(Fellow, pk=pk)
    if request.method == 'POST':
        user = fellow.user
        name = user.get_full_name()
        user.delete() # Cascade delete removes the Fellow profile
        messages.warning(request, f"Fellow {name} has been removed from the system.")
        return redirect('fellow_list')
    return render(request, 'fellows/fellow_confirm_delete.html', {'fellow': fellow})


# --- API VIEWSET (For Mobile App / External Systems) ---

class FellowViewSet(viewsets.ModelViewSet):
    """API ViewSet for Fellow management returning JSON."""
    queryset = Fellow.objects.all()
    serializer_class = FellowSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """GET /api/fellows/statistics/"""
        queryset = self.get_queryset()
        status_breakdown = {choice[0]: 0 for choice in Fellow.Status.choices}
        status_counts = queryset.values('status').annotate(total=Count('id'))
        
        for item in status_counts:
            status_breakdown[item['status']] = item['total']

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