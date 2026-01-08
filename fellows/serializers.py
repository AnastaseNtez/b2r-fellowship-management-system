# fellows/serializers.py
from rest_framework import serializers
from .models import Fellow


class FellowSerializer(serializers.ModelSerializer):
    # 1. Pull names from the User model via the 'user' relationship
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    # 2. Get the sector name from the ForeignKey relationship
    assigned_sector_name = serializers.CharField(
        source='assigned_sector.name', 
        read_only=True
    )
    
    # 3. Use your model's existing @property for the full name
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = Fellow
        fields = (
            'id', 
            'full_name', 
            'first_name', 
            'last_name',
            'university', 
            'degree_field', 
            'graduation_year', 
            'assigned_sector', 
            'assigned_sector_name', 
            'status', 
            'training_completed',
            'fellowship_start_date', 
            'fellowship_end_date',
            'user'
        )
        
        read_only_fields = ('user',)

    def create(self, validated_data):
        
        user_instance = validated_data.pop('user', None)
        if not user_instance:
             raise serializers.ValidationError("User instance must be provided.")
             
        return Fellow.objects.create(user=user_instance, **validated_data)