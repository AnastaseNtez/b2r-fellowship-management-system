from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from fellows.models import Fellow
"""
Consolidating User Management:
This script helps to see a user's role and fellowship details directly on their User page.
"""
# Define inlines to show Profile and Fellow details on the User page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Role Profile'

class FellowInline(admin.StackedInline):
    model = Fellow
    can_delete = False
    verbose_name_plural = 'Fellowship Details'

# unregister the default User admin before registering our customized version
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, FellowInline)
    
    # Add the Role to the User list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    
    def get_role(self, obj):
        # Access the linked UserProfile to show the role
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.get_role_display()
        return "No Role"
    get_role.short_description = 'System Role'