from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'content_type', 'object_id', 'start_date', 'end_date',
            'guests', 'total_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Convert content_type ID to model name in the response."""
        representation = super().to_representation(instance)
        representation['content_type'] = instance.content_type.model  # Convert ID to model name
        return representation
    
    def validate_content_type(self, value):
        """Ensure the provided content_type ID exists in ContentType."""
        if not ContentType.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Invalid content_type. Object with ID {value.id} does not exist.")
        return value
