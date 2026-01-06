from rest_framework import serializers
from .models import TrainingActivity

class TrainingActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the TrainingActivity model.
    - Provides human-readable names for Fellow and District.
    - Includes status labels for clear frontend display.
    - Calculates decimal duration from DurationField.
    - Handles photo uploads and validation logic.
    """
    
    # Readable strings for the frontend
    fellow_name = serializers.ReadOnlyField(source='fellow.user.get_full_name')
    district_name = serializers.ReadOnlyField(source='sector.district.name')
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    
    # Calculated field: Converts DurationField (timedelta) to a decimal number
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = TrainingActivity
        fields = [
            'id', 
            'fellow', 
            'fellow_name', 
            'date',
            'sector',
            'district_name', 
            'village_name',
            'training_topic', 
            'training_method', 
            'duration',          # HH:MM:SS format
            'duration_hours',    # Decimal format (e.g., 1.5)
            'number_of_farmers_trained', 
            'status', 
            'status_label',
            'is_resubmitted',
            'mentor_comments', 
            'photos',
            'created_at'
        ]
        # These fields are managed by Mentors or the system, not by the Fellow API
        read_only_fields = ['status', 'mentor_comments', 'created_at', 'is_resubmitted']

    def get_duration_hours(self, obj):
        """
        Logic to convert the model's DurationField (timedelta) 
        into a float for the API (e.g., 90 mins -> 1.5 hours).
        """
        if obj.duration:
            # total_seconds() / 3600 converts to hours
            return round(obj.duration.total_seconds() / 3600, 2)
        return 0.0

    def validate_number_of_farmers_trained(self, value):
        """API-level check to ensure data integrity for impact metrics."""
        if value < 1:
            raise serializers.ValidationError("A training session must reach at least 1 farmer.")
        return value

    def validate_date(self, value):
        """Ensures that the API does not accept future-dated logs."""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Training date cannot be in the future.")
        return value