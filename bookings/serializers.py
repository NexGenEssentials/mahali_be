from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'service_name', 'service_type', 'date', 'status', 'total_price', 'created_at', 'modified_at']
        read_only_fields = ['user', 'created_at', 'modified_at']

    def create(self, validated_data):
   
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)