from django.contrib import admin
from .models import TrainingActivity

@admin.register(TrainingActivity)
class TrainingActivityAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = (
        'training_topic', 
        'fellow', 
        'sector', 
        'date', 
        'status', 
        'number_of_farmers_trained'
    )
    
    # Filters on the right sidebar
    list_filter = ('status', 'training_method', 'date', 'sector__district')
    
    # Search functionality
    search_fields = (
        'training_topic', 
        'fellow__user__first_name', 
        'fellow__user__last_name', 
        'village_name'
    )
    
    # Organization of the edit page
    fieldsets = (
        ('General Information', {
            'fields': ('fellow', 'date', 'status')
        }),
        ('Location Details', {
            'fields': ('sector', 'village_name')
        }),
        ('Training Content', {
            'fields': (
                'training_topic', 
                'training_method', 
                'number_of_farmers_trained', 
                'duration_hours'
            )
        }),
        ('Notes & Feedback', {
            'fields': ('challenges_notes', 'success_stories', 'mentor_comments')
        }),
        ('Media', {
            'fields': ('photos',),
        }),
    )

    # Make the date tracking fields read-only
    readonly_fields = ('created_at', 'updated_at')