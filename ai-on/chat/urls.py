from django.urls import path
from .views import ChatView, ChatHistoryView, ChatResetView

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('history/', ChatHistoryView.as_view(), name='chat-history'),
    path('reset/', ChatResetView.as_view(), name='chat-reset'),
]