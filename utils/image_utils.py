from rest_framework import serializers
from django.conf import settings

class AbsoluteImageURLField(serializers.ImageField):
    def to_representation(self, value):
        if value and hasattr(value, 'url'):
            # Generate the absolute URL using the BASE_URL from settings
            return f"{settings.BASE_URL}{value.url}"
        return None
