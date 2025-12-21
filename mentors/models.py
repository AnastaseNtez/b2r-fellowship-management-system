from django.db import models
from django.contrib.auth.models import User

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    organization = models.CharField(max_length=200)
    expertise_area = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15)
    
    # Track when they joined the program
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Mentor: {self.user.get_full_name()}"

    @property
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"