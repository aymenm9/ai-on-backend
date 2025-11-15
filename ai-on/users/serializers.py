from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['onboarding_status', 'bio', 'location', 'birth_date', 'ai_summary']

class UserSerializer(ModelSerializer):
    profile = UserProfileSerializer(read_only=True, source='user_profile')
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']