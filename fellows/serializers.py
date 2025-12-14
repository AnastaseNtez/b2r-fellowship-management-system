# fellows/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Fellow
# may import serializers for other apps later, like accounts/UserProfile

class FellowSerializer(serializers.ModelSerializer):
    # Read-only field to display the full name of the assigned sector
    assigned_sector_name = serializers.CharField(
        source='assigned_sector.name', 
        read_only=True
    )
    
    # Read-only field to display the Fellow's full name (for easy reporting)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Fellow
        fields = (
            'id', 'fellow_id', 'full_name', 'first_name', 'last_name',
            'university', 'degree_field', 'graduation_year', 
            'assigned_sector', 'assigned_sector_name', 
            'status', 'training_completed',
            'fellowship_start_date', 'fellowship_end_date',
            'created_at', 'updated_at', 'user' # Include the user foreign key
        )
        read_only_fields = ('fellow_id', 'created_at', 'updated_at', 'user') # These are typically managed internally

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    # --- Custom Validation and Creation Logic (Crucial for Fellow Creation) ---
    # When creating a Fellow, a User account MUST be created simultaneously.

    def create(self, validated_data):
        # The Coordinator needs to create a Django User account first, then the Fellow profile.
        # This implementation requires the calling code (View) to handle User creation.

        # For the simplest case where the user object is passed to the serializer:
        user_data = validated_data.pop('user', None) # Remove 'user' if handled it in the view
        
        if user_data:
            # If the view already created the user, use that object
            user_instance = user_data 
        else:
            # Simple fallback if the view didn't create the user (NOT RECOMMENDED for production)
            # should handle User creation and role assignment in the ViewSet or a separate registration serializer.
            raise serializers.ValidationError("User instance must be provided during Fellow creation.")

        # Create the Fellow instance
        fellow = Fellow.objects.create(user=user_instance, **validated_data)
        return fellow