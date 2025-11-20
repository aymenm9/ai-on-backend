# Main AI Coordinator - Implementation Summary

## What Was Created

The **Main AI Coordinator** has been successfully implemented in the `ai_core` app. This agent serves as the central orchestrator for all other agents in the AION system.

## Key Design Decision

**The Main AI Coordinator has NO user-facing API endpoints.** It is designed exclusively for agent-to-agent communication. Users never interact with it directly.

**Role Update**: The Coordinator is strictly a **backend manager**. It receives directives from user-facing agents (like Chatbot), commands worker agents (like Budget Agent), and reports results back to the calling agent. It does NOT engage in conversation with the user.

### Architecture Flow

```
User → Chatbot Agent → Main AI Coordinator → Budget Agent
                                           → Other Specialized Agents
```

## Files Created/Modified

### 1. `ai_core/tools.py`
- **Purpose**: Contains function tools for agent communication
- **Key Functions**:
  - `call_budget_agent()`: Allows coordinator to call Budget Agent
  - `send_message_to_agent()`: Generic function to call any agent
  - `call_main_coordinator()`: **Allows OTHER agents to call the coordinator**
- **Function Declarations**: Gemini API function declarations for all tools

### 2. `ai_core/services.py`
- **Purpose**: Core business logic for the coordinator
- **Key Functions**:
  - `get_or_create_coordinator_agent()`: Creates/retrieves the coordinator agent
  - `process_coordinator_message()`: Main entry point for processing messages
- **Configuration**:
  - Model: `gemini-2.5-flash-8b` (Gemini 2.5 Flash-Lite as requested)
  - Thinking Budget: `0` (for fast responses)
- **System Instruction**: Strictly defined as a manager that commands worker agents and reports to calling agents.
- **Features**:
  - Multi-iteration function calling (max 5 iterations)
  - Tracks which agents were called
  - Maintains conversation history

### 3. `ai_core/views.py`
- **Purpose**: Explicitly states NO user-facing views
- **Content**: Documentation on how to use the coordinator from other agents

### 4. `ai_core/urls.py`
- **Purpose**: Empty URL patterns (no endpoints)
- **Content**: Comment explaining this is for agent-to-agent communication only

### 5. `ai_core/serializers.py`
- **Purpose**: Serializers (kept for potential future internal use)
- **Content**: Basic message serializers

### 6. `ai_core/README.md`
- **Purpose**: Comprehensive documentation
- **Sections**:
  - Architecture overview
  - How to use from other agents
  - Integration examples (chatbot)
  - How to add new agents
  - Usage examples with flow diagrams

## How Other Agents Call the Coordinator

### Method 1: Direct Import (Simple)

```python
from ai_core.services import process_coordinator_message

result = process_coordinator_message(user, "User wants to create a budget")
```

### Method 2: Gemini Function Calling (Recommended for AI Agents)

```python
from agents.services import register_agent_function
from ai_core.tools import call_main_coordinator, call_main_coordinator_declaration

# Register in your agent's get_or_create function
register_agent_function(
    agent_id=agent.id,
    func_name="call_main_coordinator",
    function_declaration=call_main_coordinator_declaration,
    function=call_main_coordinator
)
```

## Example Scenario

**User Request**: "I want to change my grocery budget to 15000 DA"

**Flow**:
1. User sends message to **Chatbot Agent** (via API)
2. Chatbot recognizes this needs coordination
3. Chatbot calls `call_main_coordinator(user, "User wants to change grocery budget to 15000 DA")`
4. Main AI Coordinator analyzes the request: "Directive received. Delegating to Budget Agent."
5. Main AI Coordinator calls `call_budget_agent(user, "Update grocery budget to 15000 DA")`
6. Budget Agent updates the budget and returns result
7. Main AI Coordinator synthesizes the response: "Budget Agent updated groceries to 15000."
8. Main AI Coordinator returns report to Chatbot
9. Chatbot presents result to user: "I've updated your grocery budget to 15,000 DA as requested."

## Currently Supported Agents

The coordinator can currently call:
- **budget_agent**: For budget generation, updates, and rebalancing

## Adding New Agents

When you create a new agent (e.g., `expense_manager`), follow these steps:

1. **Create the tool function** in `ai_core/tools.py`
2. **Create the function declaration** for Gemini
3. **Update `send_message_to_agent()`** to route to your new agent
4. **Update the enum** in `send_message_to_agent_declaration`
5. **Register the function** in `get_or_create_coordinator_agent()`
6. **Update the system instruction** to include your new agent

Detailed instructions are in `ai_core/README.md`.

## Testing

Since there's no user-facing API, test by calling from Python:

```python
from ai_core.services import process_coordinator_message
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
result = process_coordinator_message(user, "Create a monthly budget")
print(result)
```

## Next Steps

To fully utilize the Main AI Coordinator:

1. **Create/Update the Chatbot Agent** to register the `call_main_coordinator` tool
2. **Update the Chatbot's system instruction** to know when to call the coordinator
3. **Test the full flow**: User → Chatbot → Coordinator → Budget Agent

## Technical Details

- **Model**: Gemini 2.5 Flash-Lite (8B) - `gemini-2.5-flash-8b`
- **Thinking Budget**: 0 (fast responses)
- **Max Iterations**: 5 (prevents infinite loops)
- **History Tracking**: Yes (via `ConversationHistory` model)
- **Agent Tracking**: Yes (returns which agents were called)

## Benefits of This Architecture

1. **Separation of Concerns**: Users interact with chatbot, complex orchestration happens behind the scenes
2. **Scalability**: Easy to add new specialized agents
3. **Flexibility**: Coordinator can call multiple agents in sequence
4. **Transparency**: Tracks which agents were involved
5. **Maintainability**: Clear separation between user-facing and internal agents
