from django.db.models import Sum, Count
from .models import TrainingActivity

def get_program_metrics():
    # Pre-filter approved activities to reuse in multiple calculations
    approved_activities = TrainingActivity.objects.filter(status='APPROVED')
    
    return {
        'total_farmers': approved_activities.aggregate(
            Sum('number_of_farmers_trained')
        )['number_of_farmers_trained__sum'] or 0,
        
        'total_sessions': approved_activities.count(),
        
        # Count distinct sectors reached
        'active_sectors_count': approved_activities.values('sector').distinct().count(),
        
        # Break down by Province for the Donor Map
        'province_reach': list(approved_activities.values(
            'sector__district__province__name'
        ).annotate(
            total_farmers=Sum('number_of_farmers_trained'),
            session_count=Count('id')
        ).order_by('-total_farmers'))
    }