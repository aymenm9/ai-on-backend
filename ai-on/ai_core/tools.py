"""
Main AI Coordinator Tools

These are the function tools available to the Main AI Coordinator agent.
Also includes tools for OTHER agents to call the Main AI Coordinator.
"""

from typing import Optional
from django.contrib.auth.models import User


def call_budget_agent(user: User, message: str) -> dict:
    """
    Call the Budget Agent to generate or update budgets.
    
    Args:
        user: The Django User object
        message: The message/request to send to the Budget Agent
        
    Returns:
        Dictionary with the Budget Agent's response
    """
    from budget.services import process_budget_generation
    
    result = process_budget_generation(user, message)
    return result


def send_message_to_agent(
    agent_name: str,
    message: str,
    user: User
) -> dict:
    """
    Send a message to any available agent in the system.
    
    This is a generic function that routes messages to specific agents.
    Currently supports: budget_agent
    
    Args:
        agent_name: Name of the agent to call (e.g., 'budget_agent')
        message: The message/request to send to the agent
        user: The Django User object
        
    Returns:
        Dictionary with the agent's response
        
    Raises:
        ValueError: If the agent_name is not recognized
    """
    if agent_name == "budget_agent":
        return call_budget_agent(user, message)
    else:
        raise ValueError(f"Agent '{agent_name}' is not recognized or not yet implemented.")


# Function declaration for Gemini API - call_budget_agent
call_budget_agent_declaration = {
    "name": "call_budget_agent",
    "description": "Calls the Budget Agent to generate, update, or rebalance user budgets based on financial data and goals.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The request or instruction to send to the Budget Agent (e.g., 'Generate a monthly budget' or 'Update budget for groceries')."
            }
        },
        "required": ["message"]
    }
}


# Function declaration for Gemini API - send_message_to_agent
send_message_to_agent_declaration = {
    "name": "send_message_to_agent",
    "description": "Sends a message to any available agent in the AION system. Use this to delegate tasks to specialized agents.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_name": {
                "type": "string",
                "enum": ["budget_agent"],
                "description": "The name of the agent to call. Currently available: 'budget_agent'."
            },
            "message": {
                "type": "string",
                "description": "The message or request to send to the specified agent."
            }
        },
        "required": ["agent_name", "message"]
    }
}
