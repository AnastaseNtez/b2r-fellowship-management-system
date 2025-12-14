# accounts/models.py

from django.db import models
from django.contrib.auth import get_user_model

# Use the correct Django utility for defining choices
from django.db.models import TextChoices 

class UserProfile(models.Model):
    """
    Model to store additional, role-specific details for a Django User.
    """
    
    # 1. Define the Role choices using TextChoices
    class Role(TextChoices):
        # VALUE, DISPLAY_NAME
        COORDINATOR = 'COORDINATOR', 'Coordinator'
        FELLOW = 'FELLOW', 'Fellow' # <--- This defines UserProfile.Role.FELLOW
        MENTOR = 'MENTOR', 'Mentor'
        # Add other roles as needed
        

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    
    # 2. Define the role field using the choices
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FELLOW 
    )

    # Note: Ensure you run 'python manage.py makemigrations' and 'migrate' 
    # if you are adding this model or changing the role field definition.

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"