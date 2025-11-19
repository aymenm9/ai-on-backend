from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    # all info hire will be filled during onboarding process by
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    onboarding_status = models.CharField(max_length=50 , choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),], default='not_started')
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    savings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    investments = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debts = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user_ai_preferences = models.JSONField(blank=True, null=True)  # to store user AI preferences like tone, style, etc.
    personal_info = models.JSONField(blank=True, null=True)  
    extra_info = models.JSONField(blank=True, null=True)   # additional info needed by other ai's agints in the system to undrtand the user better and meat his goals 
    ai_summary = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.user.username