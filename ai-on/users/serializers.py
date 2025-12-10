from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(ModelSerializer):
    """
    Serializer for UserProfile model.
    Includes all financial data and AI preferences.
    """
    class Meta:
        model = UserProfile
        fields = [
            'onboarding_status',
            'monthly_income',
            'savings',
            'investments',
            'debts',
            'user_ai_preferences',
            'personal_info',
            'extra_info',
            'ai_summary'
        ]
        read_only_fields = ['onboarding_status', 'ai_summary']


class UserSerializer(ModelSerializer):
    """
    Serializer for User model with embedded profile.
    """
    profile = UserProfileSerializer(read_only=True, source='user_profile')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'password']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True, 'required': True}, 'username': {'required': True}}