from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Role Choices for Role-Based Access Control (RBAC)
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('coordinator', 'Program Coordinator'),
        ('fellow', 'Fellow (Field Officer)'),
        ('viewer', 'Donor/Partner Viewer'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='fellow',
        help_text="The role determines system access and permissions."
    )
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True, 
                                    help_text="For viewer/donor profiles.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    # Add helper methods to check role
    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_coordinator(self):
        return self.role == 'coordinator'
        
    @property
    def is_fellow(self):
        return self.role == 'fellow'