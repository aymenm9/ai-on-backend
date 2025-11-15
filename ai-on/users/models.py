from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    onboarding_status = models.CharField(max_length=50 , choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),], default='not_started')
    bio = models.TextField(blank=True) # to be added by the onboarding AI agent 
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    ai_summary = models.JSONField(blank=True, null=True) # to be added by the onboarding AI agent

    def __str__(self):
        return self.user.username