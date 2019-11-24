from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "role", "name")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        try:
            return get_user_model().objects.create_user(**validated_data)
        except ValueError as e:
            raise ValidationError({'message': str(e)})

    def update(self, instance, validated_data):
        """Update a user setting the password correctly and return it"""
        password = validated_data.pop("password", None)
        try:
            user = super().update(instance, validated_data)
        except ValueError as e:
            raise ValidationError({'message': str(e)})
        if password:
            user.set_password(password)
            user.save()
        return user
