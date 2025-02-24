from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email","phone", "full_name", "role"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "full_name","phone", "password", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = self.context["request"].user
        old_password = data.get("old_password")
        new_password = data.get("new_password")

       
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

       
        if old_password == new_password:
            raise serializers.ValidationError({"new_password": "New password must be different from the old one."})

      
        if len(new_password) < 8:
            raise serializers.ValidationError({"new_password": "New password must be at least 8 characters long."})

        return data
