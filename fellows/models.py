# fellows/models.py

from django.db import models
from django.contrib.auth import get_user_model

# Import models from locations app
from locations.models import Sector, District, Province

User = get_user_model()

class Fellow(models.Model):
    """
    Model to store fellowship-specific details and link to a Django User.
    """
    
    # Choices for Status field
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        COMPLETED = 'COMPLETED', 'Completed'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'

    # --- Links ---
    # One-to-one link to the Django User model (for login, email, first_name, last_name)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='fellow_profile'
    )
    
    # --- Educational Background ---
    university = models.CharField(max_length=100)
    degree_field = models.CharField(max_length=100)
    graduation_year = models.IntegerField()
    
    # --- Assignment Details ---
    # assigned_sector is the destination; the cascade logic uses district/province 
    # as temporary form fields, not model fields.
    assigned_sector = models.ForeignKey(
        Sector, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='fellows'
    )
    
    # --- Fellowship Dates & Status ---
    fellowship_start_date = models.DateField()
    fellowship_end_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.ACTIVE
    )
    
    training_completed = models.BooleanField(default=False)
    
    # --- Helper Methods ---
    
    @property
    def get_full_name(self):
        """
        Retrieves the full name from the associated User object.
        This is the CRITICAL FIX for the 'get_full_name' error in the view.
        """
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Unknown Fellow"

    @property
    def assigned_district(self):
        """Helper to get the District via the assigned Sector."""
        return self.assigned_sector.district if self.assigned_sector else None

    @property
    def assigned_province(self):
        """Helper to get the Province via the assigned Sector/District."""
        return self.assigned_sector.district.province if self.assigned_sector else None


    def __str__(self):
        return self.get_full_name

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = "Fellow"
        verbose_name_plural = "Fellows"