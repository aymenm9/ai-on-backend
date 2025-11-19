"""
Onboarding Agent Tools

These are the function tools available to the onboarding AI agent.
"""

from typing import List, Literal, Optional
from users.models import UserProfile
from django.contrib.auth.models import User


def ask_question(
    question: str, 
    question_type: Literal['direct', 'checkboxes', 'radio'], 
    options: Optional[List[str]] = None
) -> dict:
    """
    Ask a question to the user during onboarding.
    
    This function returns a structured question that will be sent to the frontend.
    The AI agent should call this function to ask one question at a time.
    
    Args:
        question: The friendly and clear question text to ask the user
        question_type: Type of question - 'direct', 'radio', or 'checkboxes'
        options: List of options (required for 'radio' and 'checkboxes', null for 'direct')
        
    Returns:
        Dictionary with question data to be serialized and sent to frontend
        
    Raises:
        ValueError: If options are missing for radio/checkboxes questions
    """
    # Validate that options are provided for radio and checkboxes
    if question_type in ['radio', 'checkboxes'] and not options:
        raise ValueError(f"Options must be provided for '{question_type}' type questions.")
    
    # Validate that options are NOT provided for direct questions
    if question_type == 'direct' and options:
        raise ValueError("Options should not be provided for 'direct' type questions.")
    
    return {
        "question": question,
        "question_type": question_type,
        "options": options
    }


# Function declaration for Gemini API
ask_question_declaration = {
    "name": "ask_question",
    "description": "Sends a structured question to the user to collect required financial information. This should be used one question at a time.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The friendly and clear question text to ask the user."
            },
            "question_type": {
                "type": "string",
                "enum": ["direct", "radio", "checkboxes"],
                "description": "The required format for the user's answer: 'direct' (free text/number), 'checkboxes' (multiple selection), or 'radio' (single selection)."
            },
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "description": "A list of selection options, only required for 'checkboxes' or 'radio' question types. Must be null for 'direct' questions."
            }
        },
        "required": ["question", "question_type"]
    }
}


def finish_onboarding_and_save_info(
    monthly_income: float,
    savings: float,
    investments: float,
    debts: float,
    user_ai_preferences: dict,
    personal_info: dict,
    extra_info: dict,
    ai_summary: str,
    user: User
) -> dict:
    """
    Save the collected onboarding information to the UserProfile.
    
    This function should be called by the AI agent when it has collected all
    necessary information and is ready to complete the onboarding process.
    
    Args:
        monthly_income: User's monthly income amount
        savings: Current savings amount
        investments: Current investment holdings
        debts: Current debt amount
        user_ai_preferences: Dict with AI preferences (risk_preference, tone, style)
        personal_info: Dict with personal info (preferred_currency, location_context)
        extra_info: Dict with additional info (goals, budget_categories, habits)
        ai_summary: 2-4 sentence summary of the user's financial profile
        user: The Django User object
        
    Returns:
        Dictionary with success message
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.monthly_income = monthly_income
    profile.savings = savings
    profile.investments = investments
    profile.debts = debts
    profile.user_ai_preferences = user_ai_preferences
    profile.personal_info = personal_info
    profile.extra_info = extra_info
    profile.ai_summary = ai_summary
    profile.onboarding_status = 'completed'
    profile.save()
    
    return {
        "success": True,
        "message": "Onboarding completed successfully"
    }


# Function declaration for Gemini API
finish_onboarding_declaration = {
    "name": "finish_onboarding_and_save_info",
    "description": "Saves the user's onboarding information including financial details, AI preferences, personal info, extra info, and AI summary. Call this when you have collected all required information.",
    "parameters": {
        "type": "object",
        "properties": {
            "monthly_income": {
                "type": "number",
                "description": "User's monthly income amount (in their preferred currency)"
            },
            "savings": {
                "type": "number",
                "description": "Current savings amount"
            },
            "investments": {
                "type": "number",
                "description": "Current investment holdings"
            },
            "debts": {
                "type": "number",
                "description": "Current debt amount"
            },
            "user_ai_preferences": {
                "type": "object",
                "description": "AI preferences including risk_preference, tone, and style",
                "properties": {
                    "risk_preference": {"type": "string"},
                    "tone": {"type": "string"},
                    "style": {"type": "string"}
                }
            },
            "personal_info": {
                "type": "object",
                "description": "Personal information including preferred_currency and location_context",
                "properties": {
                    "preferred_currency": {"type": "string"},
                    "location_context": {"type": "string"}
                }
            },
            "extra_info": {
                "type": "object",
                "description": "Additional information including goals, budget categories, and habits"
            },
            "ai_summary": {
                "type": "string",
                "description": "A 2-4 sentence summary of the user's financial profile and goals"
            }
        },
        "required": [
            "monthly_income",
            "savings",
            "investments",
            "debts",
            "user_ai_preferences",
            "personal_info",
            "extra_info",
            "ai_summary"
        ]
    }
}