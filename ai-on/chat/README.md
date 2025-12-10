# Chatbot Agent

The Chatbot Agent is the primary conversational interface in the AION personal finance management system. It provides friendly, natural language interaction with users and intelligently delegates complex tasks to specialized agents.

## Overview

The Chatbot Agent serves as the main point of contact between users and the AION system. It uses **Gemini 2.0 Flash-Lite** for fast, efficient conversations while maintaining context and personality.

## Features

- **Natural Conversation**: Friendly, warm, and personalized interactions
- **Profile Management**: Direct updates to user financial profiles
- **Intelligent Delegation**: Routes complex tasks to the Main AI Coordinator
- **Context Awareness**: Loads user profile on first message for personalized responses
- **Multi-turn Conversations**: Maintains conversation history and context
- **Tool Integration**: Seamlessly uses tools to perform actions

## Architecture

### Components

1. **services.py**: Core chatbot logic and conversation handling
2. **tools.py**: Function tools for profile editing and coordinator delegation
3. **views.py**: API endpoints for chat, history, and reset
4. **serializers.py**: Request/response serialization
5. **urls.py**: URL routing

### Available Tools

The chatbot has access to two powerful tools:

#### 1. edit_user_profile
Updates user financial information and preferences.

**Use cases:**
- "I got a raise, my income is now 50000"
- "Update my savings to 10000"
- "I paid off some debt, it's now 5000"

**Parameters:**
- `monthly_income`: Updated monthly income
- `savings`: Updated savings amount
- `investments`: Updated investments amount
- `debts`: Updated debts amount
- `personal_info`: Personal information (JSON)
- `user_ai_preferences`: AI preferences (JSON)
- `extra_info`: Additional information (JSON)

#### 2. call_main_coordinator
Delegates complex tasks to the Main AI Coordinator.

**Use cases:**
- "Create a budget for me"
- "I want to change my grocery budget to 15000"
- "Help me plan my finances for next month"
- "I overspent on entertainment"

**Parameters:**
- `message`: The request to send to the coordinator

## API Endpoints

### POST /api/chat/
Send a message to the chatbot and receive a response.

**Request:**
```json
{
  "msg": "Hello! I want to create a budget"
}
```

**Response:**
```json
{
  "msg": "Hi there! I'd be happy to help you create a budget. Let me work with our financial planning system to generate a personalized budget based on your profile..."
}
```

### GET /api/chat/history/
Retrieve the conversation history (excluding function calls).

**Response:**
```json
[
  {
    "role": "user",
    "msg": "Hello!"
  },
  {
    "role": "model",
    "msg": "Hi there! How can I help you today?"
  }
]
```

### POST /api/chat/reset/
Clear the conversation history and start fresh.

**Response:**
```json
{
  "message": "Chat history cleared successfully"
}
```

## System Instruction

The chatbot follows a comprehensive system instruction that defines:

- **Identity**: Primary conversational interface for AION
- **Role**: Engage users, answer questions, update profiles, delegate tasks
- **Tool Usage**: When to use edit_user_profile vs call_main_coordinator
- **Behavior**: Warm, friendly, personalized, clear communication
- **Context**: User profile loaded on first message

## Conversation Flow

### Example 1: Profile Update

```
User: "I got a raise! My new salary is 60000 per month"

Chatbot: [Uses edit_user_profile tool]
Response: "That's wonderful news! 🎉 I've updated your monthly income to 60,000. 
This is a great opportunity to review your budget and savings goals. Would you 
like me to help you adjust your budget to make the most of your raise?"
```

### Example 2: Budget Creation

```
User: "I want to create a budget"

Chatbot: [Uses call_main_coordinator tool]
Response: "I'd be happy to help you create a budget! Let me work with our 
financial planning system to generate a personalized budget based on your 
profile... [includes coordinator's response with budget details]"
```

### Example 3: General Conversation

```
User: "What is AION?"

Chatbot: [No tool needed]
Response: "AION is your personal AI-powered finance management system! I'm here 
to help you manage your money, create budgets, track expenses, and achieve your 
financial goals. Think of me as your friendly financial assistant who's always 
here to help. What would you like to do today?"
```

## User Profile Loading

On the **first message** of each conversation, the chatbot automatically loads the user's complete financial profile:

- Name, username, email
- Monthly income, savings, investments, debts
- Currency and location preferences
- AI preferences and personal information
- AI-generated summary

This context enables personalized, relevant responses throughout the conversation.

## Integration with Other Agents

The chatbot integrates seamlessly with the AION ecosystem:

### Main AI Coordinator
When users request complex financial operations, the chatbot delegates to the Main AI Coordinator, which orchestrates specialized agents:

```
User → Chatbot → Main AI Coordinator → Budget Agent
                                     → Forecast Agent
                                     → Other Agents
```

### Direct Tool Usage
For simple profile updates, the chatbot handles them directly without involving other agents:

```
User → Chatbot → [edit_user_profile] → User Profile Updated
```

## Model Configuration

- **Model**: Gemini 2.0 Flash-Lite
- **Temperature**: 0.9 (creative, conversational)
- **Thinking Budget**: 0 (fast responses)
- **Max Iterations**: 5 (prevents infinite loops)

## Development Notes

- All function calls are logged in conversation history
- The chatbot tracks tool usage for transparency
- Function responses are automatically incorporated into the conversation
- History excludes function calls when returned via API (only user/model messages)
- Uses lazy imports to avoid circular dependencies

## Testing

### Basic Conversation
```python
from chat.services import process_chatbot_message
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
result = process_chatbot_message(user, "Hello!")
print(result['data']['message'])
```

### Profile Update
```python
result = process_chatbot_message(user, "Update my income to 50000")
print(result['data']['message'])
```

### Budget Delegation
```python
result = process_chatbot_message(user, "Create a budget for me")
print(result['data']['message'])
```

## Future Enhancements

- Add support for voice input/output
- Implement conversation summarization for long histories
- Add sentiment analysis for better emotional intelligence
- Support for multi-language conversations
- Integration with notification system for proactive messages
- Add memory of user preferences across sessions
