from . import views
from django.urls import path


urlpatterns = [
    path('create/', views.CreateUser.as_view(), name='signup'),
    path('me/', views.MeView.as_view(), name='me'),
]