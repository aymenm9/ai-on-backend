"""
Main AI Coordinator Serializers

Serializers for the Main AI Coordinator API.
"""

from rest_framework import serializers


class CoordinatorMessageSerializer(serializers.Serializer):
    """Serializer for sending messages to the Main AI Coordinator"""
    message = serializers.CharField(
        required=True,
        help_text="The message or request to send to the Main AI Coordinator"
    )


class CoordinatorResponseSerializer(serializers.Serializer):
    """Serializer for the Main AI Coordinator's response"""
    type = serializers.CharField(help_text="Response type: 'response' or 'error'")
    data = serializers.DictField(help_text="Response data containing message and optionally agents_called")
