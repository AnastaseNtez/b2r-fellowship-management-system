from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from fellows.models import Fellow

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 1. Create the UserProfile
        profile = UserProfile.objects.create(user=instance, role='FELLOW')
        
        # 2. If they are a Fellow, create the Fellow record
        if profile.role == 'FELLOW':
            Fellow.objects.create(
                user=instance,
                first_name=instance.first_name or instance.username,
                last_name=instance.last_name or "",
                email=instance.email,
                status='active'
            )