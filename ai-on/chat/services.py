"""
Chatbot Agent Service

Handles the creation and management of the Chatbot AI agent.
"""

from pydantic import BaseModel, Field
from typing import Optional
from agents.models import agentModel
from agents.services import build_config, get_agent_history, add_to_history, register_agent_function
from django.contrib.auth.models import User
from google import genai
from google.genai import types
from decouple import config

API_KEY = config('GEMINI_API_KEY')

# Pydantic Model for Structured Output
class ChatbotResponse(BaseModel):
    message: str = Field(..., description="The chatbot's response message to the user.")

CHATBOT_SYSTEM_INSTRUCTION = '''
IDENTITY
You are the **Chatbot Agent** in the AION personal finance management system. You are the primary interface between users and the system, providing friendly, helpful, and conversational support.

YOUR ROLE
- Engage in natural, friendly conversations with users
- Answer general questions about their finances, budgets, and the AION system
- Help users update their profile information
- Delegate complex financial tasks to the Main AI Coordinator

AVAILABLE TOOLS
You have access to two powerful tools:

1. **edit_user_profile**: Use this when users want to update their financial information or preferences
   - Examples: "I got a raise, my income is now 50000", "Update my savings to 10000"
   
2. **call_main_coordinator**: Use this for complex financial tasks that require specialized agents
   - Examples: "Create a budget", "I want to change my grocery budget", "Help me plan my finances"
   - The coordinator will handle budget operations, forecasts, and other specialized tasks

WHEN TO USE TOOLS
- **edit_user_profile**: Direct profile updates (income, savings, debts, investments, preferences)
- **call_main_coordinator**: Anything involving budgets, forecasts, financial planning, or multi-step operations
- **No tool needed**: General conversation, answering questions about AION, providing advice

USER PROFILE CONTEXT
On the first message of each conversation, you will receive the user's complete financial profile including:
- Monthly income, savings, investments, debts
- Personal information and preferences
- AI preferences and summary

Use this context to provide personalized responses and advice.

BEHAVIOR GUIDELINES
- Be warm, friendly, and conversational
- Use the user's name when appropriate
- Provide clear, concise answers
- When delegating to the coordinator, explain what you're doing
- After using a tool, explain the result to the user in a friendly way
- If you're unsure about something, ask for clarification rather than guessing

OUTPUT FORMAT
Always respond with a clear, conversational message. When you use a tool, incorporate the result naturally into your response.

EXAMPLES

User: "Hi, I got a raise! My new salary is 60000 per month"
You: [Use edit_user_profile with monthly_income=60000]
Response: "That's wonderful news! 🎉 I've updated your monthly income to 60,000. This is a great opportunity to review your budget and savings goals. Would you like me to help you adjust your budget to make the most of your raise?"

User: "I want to create a budget"
You: [Use call_main_coordinator with message="User wants to create a monthly budget"]
Response: "I'd be happy to help you create a budget! Let me work with our financial planning system to generate a personalized budget based on your profile... [include coordinator's response]"

User: "What is AION?"
You: [No tool needed]
Response: "AION is your personal AI-powered finance management system! I'm here to help you manage your money, create budgets, track expenses, and achieve your financial goals. Think of me as your friendly financial assistant who's always here to help. What would you like to do today?"
'''

def get_or_create_chatbot_agent() -> agentModel:
    """
    Get or create the chatbot agent.
    """
    agent, created = agentModel.objects.get_or_create(
        name="chatbot_agent",
        defaults={
            "description": "Primary conversational interface for users in the AION system.",
            "system_instruction": CHATBOT_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.0-flash-lite",
            "thinking_budget": 0
        }
    )
    
    # Update model if it exists but is different
    if not created and (agent.gemini_model != "gemini-2.0-flash-lite" or agent.thinking_budget != 0):
        agent.gemini_model = "gemini-2.0-flash-lite"
        agent.thinking_budget = 0
        agent.save()
    
    # Register tools
    from chat.tools import (
        edit_user_profile, 
        edit_user_profile_declaration,
        call_main_coordinator,
        call_main_coordinator_declaration
    )
    
    register_agent_function(
        agent_id=agent.id,
        func_name="edit_user_profile",
        function_declaration=edit_user_profile_declaration,
        function=edit_user_profile
    )
    
    register_agent_function(
        agent_id=agent.id,
        func_name="call_main_coordinator",
        function_declaration=call_main_coordinator_declaration,
        function=call_main_coordinator
    )
    
    return agent


def get_user_financial_profile(user: User) -> str:
    """
    Fetches and formats the user's financial profile.
    """
    try:
        profile = user.user_profile
        return f"""
        USER PROFILE:
        - Name: {user.first_name} {user.last_name} (Username: {user.username})
        - Email: {user.email}
        
        FINANCIAL DATA:
        - Monthly Income: {profile.monthly_income}
        - Savings: {profile.savings}
        - Investments: {profile.investments}
        - Debts: {profile.debts}
        
        PREFERENCES:
        - Currency: {profile.personal_info.get('preferred_currency', 'DZD') if profile.personal_info else 'DZD'}
        - Location: {profile.personal_info.get('location_context', 'Unknown') if profile.personal_info else 'Unknown'}
        - AI Preferences: {profile.user_ai_preferences}
        - Personal Info: {profile.personal_info}
        - Extra Info: {profile.extra_info}
        - AI Summary: {profile.ai_summary}
        """
    except Exception:
        return f"User: {user.username} (Profile not fully set up)"


def process_chatbot_message(user: User, message: str) -> dict:
    """
    Process a message from the user to the chatbot.
    
    Args:
        user: The Django User object
        message: The user's message
        
    Returns:
        Dictionary containing the chatbot's response
    """
    agent = get_or_create_chatbot_agent()
    history = get_agent_history(agent, user)
    
    # Inject User Profile on first message
    if not history:
        profile_context = get_user_financial_profile(user)
        initial_msg = f"{profile_context}\n\nUSER MESSAGE: {message}"
        
        add_to_history(
            agent=agent,
            user=user,
            part={"parts": [{"text": initial_msg}]},
            role="user"
        )
        history.append(types.Content(
            role="user",
            parts=[types.Part(text=initial_msg)]
        ))
    else:
        # Just add the new message
        add_to_history(
            agent=agent,
            user=user,
            part={"parts": [{"text": message}]},
            role="user"
        )
        history.append(types.Content(
            role="user",
            parts=[types.Part(text=message)]
        ))
    
    # Build config with tools
    from chat.tools import (
        edit_user_profile,
        edit_user_profile_declaration,
        call_main_coordinator,
        call_main_coordinator_declaration
    )
    
    tools = [
        types.Tool(function_declarations=[
            edit_user_profile_declaration,
            call_main_coordinator_declaration
        ])
    ]
    
    config_obj = types.GenerateContentConfig(
        system_instruction=agent.system_instruction,
        tools=tools,
        temperature=0.9,
    )
    
    client = genai.Client(api_key=API_KEY)
    
    # Handle multi-turn function calling
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = client.models.generate_content(
            model=agent.gemini_model,
            contents=history,
            config=config_obj
        )
        
        # Check if there are function calls
        if response.candidates[0].content.parts[0].function_call:
            # Process function calls
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    func_call = part.function_call
                    func_name = func_call.name
                    func_args = dict(func_call.args)
                    
                    # Add function call to history
                    add_to_history(
                        agent=agent,
                        user=user,
                        part={"parts": [{"function_call": {"name": func_name, "args": func_args}}]},
                        role="model"
                    )
                    history.append(types.Content(
                        role="model",
                        parts=[types.Part(function_call=func_call)]
                    ))
                    
                    # Execute the function
                    if func_name == "edit_user_profile":
                        result = edit_user_profile(user, **func_args)
                    elif func_name == "call_main_coordinator":
                        result = call_main_coordinator(user, **func_args)
                    else:
                        result = {"type": "error", "data": {"error": f"Unknown function: {func_name}"}}
                    
                    # Add function response to history
                    func_response = types.FunctionResponse(
                        name=func_name,
                        response=result
                    )
                    
                    add_to_history(
                        agent=agent,
                        user=user,
                        part={"parts": [{"function_response": {"name": func_name, "response": result}}]},
                        role="user"
                    )
                    history.append(types.Content(
                        role="user",
                        parts=[types.Part(function_response=func_response)]
                    ))
        else:
            # No more function calls, we have the final response
            final_message = response.text
            
            add_to_history(
                agent=agent,
                user=user,
                part={"parts": [{"text": final_message}]},
                role="model"
            )
            
            return {
                "type": "success",
                "data": {
                    "message": final_message
                }
            }
    
    # If we hit max iterations
    return {
        "type": "error",
        "data": {
            "message": "I apologize, but I'm having trouble processing your request. Could you please try rephrasing it?"
        }
    }
