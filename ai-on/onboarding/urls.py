from django.urls import path
from .views import OnboardingView, OnboardingResetView

urlpatterns = [
    path('', OnboardingView.as_view(), name='onboarding'),
    path('reset/', OnboardingResetView.as_view(), name='onboarding-reset'),
]
