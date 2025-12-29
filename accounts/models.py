# accounts/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import TextChoices 
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class UserProfile(models.Model):
    """
    Model to store additional, role-specific details for a Django User.
    """
    
    class Role(TextChoices):
        ADMIN = 'ADMIN', 'Admin'              # Added for Superusers/Staff
        COORDINATOR = 'COORDINATOR', 'Coordinator'
        FELLOW = 'FELLOW', 'Fellow'
        MENTOR = 'MENTOR', 'Mentor'
        VIEWER = 'VIEWER', 'Viewer'           # Added for Donors/Partners

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FELLOW 
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"


# --- SIGNALS FOR AUTO-SYNC ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a UserProfile when a User is created.
    If the user is a Superuser, it defaults the role to ADMIN.
    """
    if created:
        # Determine default role: Superusers become ADMIN, others become FELLOW
        default_role = UserProfile.Role.ADMIN if instance.is_superuser else UserProfile.Role.FELLOW
        UserProfile.objects.create(user=instance, role=default_role)
    else:
        # If an existing user is promoted to superuser, ensure their profile matches
        if instance.is_superuser:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            if profile.role != UserProfile.Role.ADMIN:
                profile.role = UserProfile.Role.ADMIN
                profile.save()