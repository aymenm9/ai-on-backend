"""
Main AI Coordinator Service

Handles the creation and management of the Main AI Coordinator agent.
This agent acts as the central orchestrator for all other agents in the AION system.
"""

from agents.models import agentModel
from agents.services import register_agent_function, build_config, execute_function, get_agent_history, add_to_history
from .tools import (
    call_budget_agent,
    call_budget_agent_declaration,
    send_message_to_agent,
    send_message_to_agent_declaration
)
from django.contrib.auth.models import User
from google import genai
from google.genai import types
from decouple import config

API_KEY = config('GEMINI_API_KEY')

COORDINATOR_SYSTEM_INSTRUCTION = '''
IDENTITY
You are the **Main AI Coordinator** in the AION personal finance management system. You are the central intelligence that orchestrates all other specialized agents to provide comprehensive financial guidance and support to users.

THE AION SYSTEM CONTEXT
AION is a multi-agent personal finance management application designed to help users manage their finances effectively. The system consists of multiple specialized agents, each with specific expertise:
- **Budget Agent**: Creates, updates, and rebalances user budgets
- **Onboarding Agent**: Collects initial financial information from new users
- **Chatbot Agent**: Handles general user conversations (you may interact with this)
- **Market Watcher**: Monitors market trends and opportunities (future)
- **Planner & Forecaster**: Provides financial planning and forecasting (future)
- **Expense Manager**: Tracks and categorizes expenses (future)
- **Product Advisor**: Recommends financial products (future)
- **Notification Agent**: Sends alerts and reminders (future)

YOUR ROLE IN THE SYSTEM
You are the **brain** of AION. When a user makes a request, you:
1. **Analyze** the user's request and context
2. **Decide** which specialized agent(s) should handle the task
3. **Delegate** tasks to the appropriate agents using your tools
4. **Synthesize** responses from multiple agents if needed
5. **Communicate** the final result to the user in a clear, helpful manner

AVAILABLE TOOLS
You have access to the following tools to delegate tasks:
- `call_budget_agent(message)`: Call the Budget Agent for budget-related tasks
- `send_message_to_agent(agent_name, message)`: Generic function to call any agent

WHAT YOU DO
* Understand user requests and their financial context
* Route requests to the most appropriate specialized agent(s)
* Coordinate between multiple agents when a task requires multiple steps
* Provide clear, actionable responses to users
* Maintain context across conversations
* Explain what you're doing and why

WHAT YOU DON'T DO
* Don't try to generate budgets yourself - delegate to the Budget Agent
* Don't collect onboarding information - that's the Onboarding Agent's job
* Don't make assumptions - ask for clarification if needed
* Don't perform tasks that specialized agents are designed for

DECISION MAKING
When you receive a user request:
1. **Budget-related requests** → Call Budget Agent
   - Examples: "Create a budget", "Update my grocery budget", "I overspent on dining"
2. **General financial questions** → Answer directly if simple, or delegate if complex
3. **Multi-step tasks** → Break down and coordinate between agents

PERSONALITY & TONE
- Professional yet friendly and approachable
- Clear and concise in explanations
- Proactive in suggesting helpful actions
- Transparent about what you're doing (e.g., "I'm calling the Budget Agent to...")
- Patient and understanding

RESPONSE STYLE
- Always acknowledge the user's request
- Explain which agent you're calling and why
- Provide context from agent responses
- Offer follow-up suggestions when appropriate
- Use the user's preferred communication style (from their profile if available)
'''


def get_or_create_coordinator_agent() -> agentModel:
    """
    Get or create the Main AI Coordinator agent and register its functions.
    
    Returns:
        The coordinator agent model instance
    """
    agent, created = agentModel.objects.get_or_create(
        name="main_ai_coordinator",
        defaults={
            "description": "Central orchestrator that coordinates all specialized agents in the AION system",
            "system_instruction": COORDINATOR_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.5-flash-8b",
            "thinking_budget": 0
        }
    )
    
    # Update model if it exists but configuration is different
    if not created and (agent.gemini_model != "gemini-2.5-flash-8b" or agent.thinking_budget != 0):
        agent.gemini_model = "gemini-2.5-flash-8b"
        agent.thinking_budget = 0
        agent.save()
    
    # Register functions
    register_agent_function(
        agent_id=agent.id,
        func_name="call_budget_agent",
        function_declaration=call_budget_agent_declaration,
        function=call_budget_agent
    )
    
    register_agent_function(
        agent_id=agent.id,
        func_name="send_message_to_agent",
        function_declaration=send_message_to_agent_declaration,
        function=send_message_to_agent
    )
    
    return agent


def process_coordinator_message(user: User, user_message: str) -> dict:
    """
    Process a message sent to the Main AI Coordinator.
    
    Args:
        user: The Django User object
        user_message: The user's message/request
        
    Returns:
        Dictionary with either:
        - {"type": "response", "data": {"message": str, "agent_called": str|None}}
        - {"type": "error", "data": {"error": str}}
    """
    # Get or create agent
    agent = get_or_create_coordinator_agent()
    
    # Get conversation history
    history = get_agent_history(agent, user)
    
    # Add user message to history
    add_to_history(
        agent=agent,
        user=user,
        part={"parts": [{"text": user_message}]},
        role="user"
    )
    history.append(types.Content(
        role="user",
        parts=[types.Part(text=user_message)]
    ))
    
    # Build config
    config_obj = build_config(agent)
    
    # Create Gemini client
    client = genai.Client(api_key=API_KEY)
    
    # Track which agents were called
    agents_called = []
    
    # Generate response (may involve multiple function calls)
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = client.models.generate_content(
            model=agent.gemini_model,
            contents=history,
            config=config_obj
        )
        
        # Check if there are function calls
        has_function_call = False
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    has_function_call = True
                    func_call = part.function_call
                    func_name = func_call.name
                    func_args = dict(func_call.args)
                    
                    # Add user to args
                    func_args['user'] = user
                    
                    # Track which agent is being called
                    if func_name == "call_budget_agent":
                        agents_called.append("budget_agent")
                    elif func_name == "send_message_to_agent":
                        agents_called.append(func_args.get('agent_name', 'unknown'))
                    
                    # Execute the function
                    result = execute_function(agent, func_name, func_args)
                    
                    # Add function call to history
                    add_to_history(
                        agent=agent,
                        user=user,
                        part={"parts": [{"function_call": {"name": func_name, "args": func_args}}]},
                        role="model"
                    )
                    
                    # Add function response to history
                    add_to_history(
                        agent=agent,
                        user=user,
                        part={"parts": [{"function_response": {"name": func_name, "response": result}}]},
                        role="user"
                    )
                    
                    # Update history for next iteration
                    history.append(types.Content(
                        role="model",
                        parts=[types.Part(function_call=types.FunctionCall(name=func_name, args=func_args))]
                    ))
                    history.append(types.Content(
                        role="user",
                        parts=[types.Part(function_response=types.FunctionResponse(name=func_name, response=result))]
                    ))
        
        # If no function call, we have the final response
        if not has_function_call:
            # Save model response to history
            add_to_history(
                agent=agent,
                user=user,
                part={"parts": [{"text": response.text if response.text else ""}]},
                role="model"
            )
            
            return {
                "type": "response",
                "data": {
                    "message": response.text if response.text else "I've processed your request.",
                    "agents_called": agents_called if agents_called else None
                }
            }
    
    # If we hit max iterations, return what we have
    return {
        "type": "error",
        "data": {
            "error": "Maximum iterations reached. Please try again with a simpler request."
        }
    }
