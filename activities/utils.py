from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth # <-- Add this
from .models import TrainingActivity

def get_program_metrics():
    approved_activities = TrainingActivity.objects.filter(status='APPROVED')
    
    # --- Monthly Trends for Chart.js ---
    # Grouping by month and summing farmers
    monthly_trends = list(approved_activities.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('number_of_farmers_trained')
    ).order_by('month'))

    return {
        'total_farmers': approved_activities.aggregate(
            Sum('number_of_farmers_trained')
        )['number_of_farmers_trained__sum'] or 0,
        
        'total_sessions': approved_activities.count(),
        
        'active_sectors_count': approved_activities.values('sector').distinct().count(),
        
        'province_reach': list(approved_activities.values(
            'sector__district__province__name'
        ).annotate(
            total_farmers=Sum('number_of_farmers_trained'),
            session_count=Count('id')
        ).order_by('-total_farmers')),

        # --- New Fields for API/Charts ---
        'chart_labels': [item['month'].strftime('%b %Y') for item in monthly_trends],
        'chart_values': [item['total'] for item in monthly_trends],
    }