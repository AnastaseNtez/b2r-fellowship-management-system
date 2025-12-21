from django.contrib import admin
from .models import Fellow

@admin.register(Fellow)
class FellowAdmin(admin.ModelAdmin):
    # 1. Added 'mentor' to the columns list
    list_display = (
        'get_full_name', 
        'mentor', # Shows the mentor in the main list
        'get_email', 
        'university', 
        'display_location', 
        'status', 
    )
    
    # 2. Added 'mentor' to filters
    list_filter = (
        'mentor', # Allows you to filter fellows by their mentor
        'status', 
        'training_completed', 
        'assigned_sector__district__province', 
    )
    
    search_fields = (
        'user__first_name', 
        'user__last_name', 
        'mentor__user__first_name', # Can search for a mentor's fellows
        'user__email', 
    )
    
    # 3. CRITICAL: Adding 'mentor' to the Edit Page sections
    fieldsets = (
        ('Personal Info', {
            'fields': ('user',)
        }),
        ('Education', {
            'fields': ('university', 'degree_field', 'graduation_year')
        }),
        ('Assignment', {
            # Add 'mentor' here to make the dropdown appear!
            'fields': ('mentor', 'assigned_sector', 'status', 'training_completed')
        }),
        ('Dates', {
            'fields': ('fellowship_start_date', 'fellowship_end_date')
        }),
    )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def display_location(self, obj):
        if obj.assigned_sector:
            return f"{obj.assigned_sector} ({obj.assigned_district})"
        return "Not Assigned"
    display_location.short_description = 'Assignment (Sector/District)'

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Fellow Name'
    get_full_name.admin_order_field = 'user__first_name'