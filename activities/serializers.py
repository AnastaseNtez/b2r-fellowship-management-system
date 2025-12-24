""" 
This script converts the complex activity model into a clean JSON
"""

from rest_framework import serializers
from .models import TrainingActivity

class TrainingActivitySerializer(serializers.ModelSerializer):
    # Flattening data for the API consumer (e.g., getting names instead of IDs)
    fellow_name = serializers.ReadOnlyField(source='fellow.get_full_name')
    sector_name = serializers.ReadOnlyField(source='sector.name')
    district_name = serializers.ReadOnlyField(source='sector.district.name')

    class Meta:
        model = TrainingActivity
        fields = [
            'id', 'fellow', 'fellow_name', 'date', 'sector', 'sector_name', 
            'district_name', 'village_name', 'number_of_farmers_trained', 
            'training_topic', 'training_method', 'duration_hours', 
            'status', 'mentor_comments', 'photos'
        ]
        # These fields are set by the system, not the user
        read_only_fields = ['fellow', 'status', 'mentor_comments']