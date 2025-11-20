"""
Main AI Coordinator Views

The Main AI Coordinator does NOT have user-facing views.
It is only called by other agents (like the chatbot) for coordination tasks.

To use the coordinator from another agent, import and call:
    from ai_core.services import process_coordinator_message
    result = process_coordinator_message(user, message)
"""

from django.shortcuts import render

# No views - this agent is only for agent-to-agent communication
