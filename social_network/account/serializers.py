from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FriendRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.ReadOnlyField(source='from_user.username')
    to_user = serializers.ReadOnlyField(source='to_user.username')

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'created_at', 'is_accepted']