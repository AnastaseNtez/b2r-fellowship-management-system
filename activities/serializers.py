from rest_framework import serializers
from .models import TrainingActivity

class TrainingActivitySerializer(serializers.ModelSerializer):
    fellow_name = serializers.ReadOnlyField(source='fellow.user.get_full_name')
    district_name = serializers.ReadOnlyField(source='sector.district.name')

    class Meta:
        model = TrainingActivity
        fields = [
            'id', 'fellow', 'fellow_name', 'district_name', 
            'training_topic', 'date', 'number_of_farmers_trained', 
            'training_method', 'duration_hours', 'status', 
            'mentor_comments', 'created_at'
        ]
        read_only_fields = ['status', 'mentor_comments', 'created_at']