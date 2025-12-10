from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for incoming chat messages."""
    msg = serializers.CharField(required=True, help_text="The user's message to the chatbot")


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chatbot responses."""
    msg = serializers.CharField(help_text="The chatbot's response message")


class ChatHistoryItemSerializer(serializers.Serializer):
    """Serializer for a single chat history item."""
    role = serializers.CharField(help_text="Either 'user' or 'model'")
    msg = serializers.CharField(help_text="The message content")
