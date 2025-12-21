from django.contrib import admin
from .models import Mentor

# to ensure we can manage Mentors easily, we'll add them to the admin site.
@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'organization', 'expertise_area', 'joined_date')
    search_fields = ('user__first_name', 'user__last_name', 'organization')