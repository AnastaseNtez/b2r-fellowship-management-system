from django.db import models
from fellows.models import Fellow   # Used for the Fellow link
from locations.models import Sector # Used for the Sector link

class TrainingActivity(models.Model):
    # FK1: Link to the Fellow who logged the activity
    fellow = models.ForeignKey(
        Fellow, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )

    # Activity Details
    date = models.DateField()
    
    # FK2: Location of the Training Activity
    sector = models.ForeignKey(
        Sector, 
        on_delete=models.PROTECT, # Prevent deleting a Sector if it has associated activities
        related_name='training_activities'
    )
    village_name = models.CharField(max_length=100)
    
    number_of_farmers_trained = models.IntegerField()
    
    # Core Data Fields
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

    # Date Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'sector__name']
        verbose_name_plural = "Training Activities"

    def __str__(self):
        return f"Activity by {self.fellow.last_name} on {self.date}"