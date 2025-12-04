from django.db import models
from django.contrib.auth.models import User  # Used for the OneToOne link
from locations.models import Sector         # Used for the Foreign Key link

class Fellow(models.Model):
    # FK1: OneToOne Link to the User (required for login/permissions)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fellow_profile')

    # Unique Identifier
    fellow_id = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique identifier, e.g., FEL-2024-001"
    )
    
    # Personal Information (redundant to User model, but simplifies data access)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Educational Background
    university = models.CharField(max_length=100)
    degree_field = models.CharField(max_length=100)
    graduation_year = models.IntegerField()

    # FK2: Assignment Location
    assigned_sector = models.ForeignKey(
        Sector, 
        on_delete=models.SET_NULL, # If a sector is deleted, keep the fellow record but set the sector to NULL
        related_name='fellows',
        null=True,
        blank=True
    )

    # Status Fields
    FELLOW_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_leave', 'On Leave'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=FELLOW_STATUS_CHOICES, 
        default='active'
    )
    training_completed = models.BooleanField(
        default=False, 
        help_text="Has completed the initial Land of Goshen training."
    )

    # Date Tracking
    fellowship_start_date = models.DateField()
    fellowship_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fellow_id']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.fellow_id})"