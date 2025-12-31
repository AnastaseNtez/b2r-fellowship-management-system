from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from fellows.models import Fellow   
from locations.models import Sector 

def validate_not_future(value):
    """
    Validator to ensure training sessions are not logged for future dates.
    This maintains the integrity of the impact reporting system.
    """
    if value > timezone.now().date():
        raise ValidationError("The date cannot be in the future.")

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

    # Date with future-date protection
    date = models.DateField(validators=[validate_not_future])
    
    # FK2: Location of the Training Activity
    sector = models.ForeignKey(
        Sector, 
        on_delete=models.PROTECT, 
        related_name='training_activities'
    )
    village_name = models.CharField(max_length=100)
    
    # Ensures positive integer; prevents negative farmer counts in analytics
    number_of_farmers_trained = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="You must train at least one farmer.")]
    )
    
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

    # Duration limits to prevent typos (e.g., 88 hours)
    duration_hours = models.FloatField(
        help_text="Duration of the training session in hours (e.g., 2.5)",
        validators=[
            MinValueValidator(0.1, message="Duration must be greater than 0."),
            MaxValueValidator(12.0, message="Duration cannot exceed 12 hours.")
        ]
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
        return f"Activity by {self.fellow.user.get_full_name()} on {self.date}"