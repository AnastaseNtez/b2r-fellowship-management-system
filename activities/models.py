from django.db import models
from fellows.models import Fellow   
from locations.models import Sector 

class TrainingActivity(models.Model):
    """
    Model representing a training session conducted by a Fellow.
    Includes fields for tracking data, location, and mentor approval status.
    """

    # --- Status Choices ---
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        REVISION = 'REVISION', 'Needs Revision'

    # FK1: Link to the Fellow who logged the activity
    fellow = models.ForeignKey(
        Fellow, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )

    date = models.DateField()
    
    # FK2: Location of the Training Activity
    sector = models.ForeignKey(
        Sector, 
        on_delete=models.PROTECT, 
        related_name='training_activities'
    )
    village_name = models.CharField(max_length=100)
    number_of_farmers_trained = models.IntegerField()
    
    training_topic = models.CharField(
        max_length=255, 
        help_text="e.g., Mulching, Crop Rotation, Soil Conservation"
    )
    
    METHOD_CHOICES = [
        ('demonstration', 'Demonstration'),
        ('field_visit', 'Field Visit'),
        ('group_session', 'Group Session'),
        ('workshop', 'Workshop'),
    ]
    training_method = models.CharField(
        max_length=50, 
        choices=METHOD_CHOICES
    )
    duration_hours = models.FloatField(
        help_text="Duration of the training session in hours (e.g., 2.5)"
    )

    # Optional Notes and Media
    challenges_notes = models.TextField(blank=True, null=True)
    success_stories = models.TextField(blank=True, null=True)
    photos = models.ImageField(upload_to='training_photos/', blank=True, null=True)

    # --- Mentor Approval Fields ---
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        help_text="The current approval status of this report."
    )
    
    # Flag to track if the fellow updated an activity after a revision request
    is_resubmitted = models.BooleanField(default=False)

    # Mentor feedback field to help Fellows understand required updates
    mentor_comments = models.TextField(
        blank=True, 
        null=True,
        help_text="Feedback provided by the assigned Mentor."
    )

    # Date Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'sector__name']
        verbose_name_plural = "Training Activities"

    def __str__(self):
        # Utilizes the get_full_name property from the Fellow model
        return f"Activity by {self.fellow.get_full_name} on {self.date}"