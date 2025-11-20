# Main AI Coordinator

The Main AI Coordinator is the central intelligence of the AION personal finance management system. It orchestrates all specialized agents and coordinates complex multi-agent workflows.

## Overview

The Main AI Coordinator acts as the "brain" of AION, analyzing user requests and delegating tasks to the most appropriate specialized agents. It uses **Gemini 2.5 Flash-Lite (8B)** for fast, efficient coordination.

**Important**: The Main AI Coordinator does **NOT** have a user-facing API endpoint. Users never interact with it directly. Instead, other agents (like the chatbot) call the coordinator when they need to orchestrate complex tasks.

## Architecture Flow

```
User → Chatbot Agent → Main AI Coordinator → Budget Agent
                                           → Other Agents (future)
```

**Example Scenario**:
1. User tells chatbot: "I want to change my grocery budget to 15000 DA"
2. Chatbot recognizes this requires budget modification
3. Chatbot calls `call_main_coordinator(user, "User wants to change grocery budget to 15000 DA")`
4. Main AI Coordinator analyzes the request
5. Main AI Coordinator calls Budget Agent to update the budget
6. Main AI Coordinator returns the result to Chatbot
7. Chatbot presents the result to the user

## Features

- **Intelligent Request Routing**: Analyzes requests and routes them to the appropriate specialized agents
- **Multi-Agent Coordination**: Coordinates workflows that require multiple agents
- **Context Awareness**: Maintains conversation history and user context
- **Extensible Architecture**: Easy to add new agents to the system
- **Agent-to-Agent Communication**: Designed for inter-agent messaging, not direct user interaction

## Architecture

### Components

1. **services.py**: Core business logic for the coordinator
2. **tools.py**: Function tools that allow:
   - The coordinator to call other agents (Budget Agent, etc.)
   - Other agents to call the coordinator
3. **views.py**: Empty - no user-facing endpoints
4. **serializers.py**: Not used (kept for potential future internal use)

### Agent Communication

#### For the Main AI Coordinator to call other agents:

1. **Direct Function Calls**: `call_budget_agent(message)` - Specific to Budget Agent
2. **Generic Messaging**: `send_message_to_agent(agent_name, message)` - For any agent

#### For other agents to call the Main AI Coordinator:

Use the `call_main_coordinator` function from `ai_core.tools`:

```python
from ai_core.tools import call_main_coordinator

# In your agent's code (e.g., chatbot)
result = call_main_coordinator(user, "User wants to adjust budget based on overspending")
```

## How to Use from Other Agents

### Option 1: Direct Python Import (Recommended)

```python
from ai_core.services import process_coordinator_message

# In your agent's service layer
result = process_coordinator_message(user, "User wants to create a monthly budget")
```

### Option 2: Using the Tool Function (For Gemini Function Calling)

If you're building an agent that uses Gemini function calling, register the `call_main_coordinator` tool:

```python
from agents.services import register_agent_function
from ai_core.tools import call_main_coordinator, call_main_coordinator_declaration

# In your agent's get_or_create function
register_agent_function(
    agent_id=agent.id,
    func_name="call_main_coordinator",
    function_declaration=call_main_coordinator_declaration,
    function=call_main_coordinator
)
```

Then the Gemini model can call it automatically when needed.

## Currently Supported Agents

- **budget_agent**: Generates, updates, and rebalances user budgets

## Example: Integrating with Chatbot Agent

Here's how you would integrate the Main AI Coordinator with a chatbot agent:

```python
# In chatbot/services.py

from agents.services import register_agent_function
from ai_core.tools import call_main_coordinator, call_main_coordinator_declaration

CHATBOT_SYSTEM_INSTRUCTION = '''
You are the Chatbot Agent in AION. When users ask about budgets, expenses, 
or complex financial tasks, use the call_main_coordinator function to delegate 
to the Main AI Coordinator.

Examples of when to call the coordinator:
- "I want to change my budget"
- "Help me plan my finances"
- "I overspent this month"
'''

def get_or_create_chatbot_agent():
    agent, created = agentModel.objects.get_or_create(
        name="chatbot_agent",
        defaults={
            "description": "Handles general user conversations",
            "system_instruction": CHATBOT_SYSTEM_INSTRUCTION,
            "gemini_model": "gemini-2.0-flash",
            "thinking_budget": 0
        }
    )
    
    # Register the coordinator tool
    register_agent_function(
        agent_id=agent.id,
        func_name="call_main_coordinator",
        function_declaration=call_main_coordinator_declaration,
        function=call_main_coordinator
    )
    
    return agent
```

## Usage Examples

### Example 1: Budget Creation Flow

```
User → Chatbot: "Create a monthly budget for me"
Chatbot → Main AI Coordinator: "User wants to create a monthly budget"
Main AI Coordinator → Budget Agent: "Generate budget based on user profile"
Budget Agent → Main AI Coordinator: {budget data}
Main AI Coordinator → Chatbot: "I've created a budget with 5 categories..."
Chatbot → User: "I've created a budget with 5 categories..."
```

### Example 2: Budget Update Flow

```
User → Chatbot: "I want to change my grocery budget to 15000 DA"
Chatbot → Main AI Coordinator: "User wants to change grocery budget to 15000 DA"
Main AI Coordinator → Budget Agent: "Update grocery budget to 15000 DA"
Budget Agent → Main AI Coordinator: {updated budget data}
Main AI Coordinator → Chatbot: "I've updated your grocery budget..."
Chatbot → User: "I've updated your grocery budget..."
```

## Adding New Agents

When you create a new agent, follow these steps to make it callable by the Main AI Coordinator:

### 1. Create the Agent's Tool Function

In `ai_core/tools.py`, add a new function:

```python
def call_your_agent(user: User, message: str) -> dict:
    """
    Call Your Agent to perform specific tasks.
    """
    from your_app.services import process_your_agent_task
    
    result = process_your_agent_task(user, message)
    return result
```

### 2. Create the Function Declaration

Add the Gemini function declaration:

```python
call_your_agent_declaration = {
    "name": "call_your_agent",
    "description": "Calls Your Agent to perform specific tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The request to send to Your Agent."
            }
        },
        "required": ["message"]
    }
}
```

### 3. Update the Generic Function

In `send_message_to_agent()`, add your agent to the routing logic:

```python
def send_message_to_agent(agent_name: str, message: str, user: User) -> dict:
    if agent_name == "budget_agent":
        return call_budget_agent(user, message)
    elif agent_name == "your_agent":  # Add this
        return call_your_agent(user, message)
    else:
        raise ValueError(f"Agent '{agent_name}' is not recognized.")
```

### 4. Update the Function Declaration Enum

In `send_message_to_agent_declaration`, add your agent to the enum:

```python
"agent_name": {
    "type": "string",
    "enum": ["budget_agent", "your_agent"],  # Add your agent here
    "description": "The name of the agent to call."
}
```

### 5. Register the Function

In `ai_core/services.py`, register your new function:

```python
register_agent_function(
    agent_id=agent.id,
    func_name="call_your_agent",
    function_declaration=call_your_agent_declaration,
    function=call_your_agent
)
```

### 6. Update the System Instruction

In `COORDINATOR_SYSTEM_INSTRUCTION`, add your agent to the list of available agents and update the decision-making section.

## Development Notes

- The coordinator uses a maximum of 5 iterations to prevent infinite loops
- All function calls are logged in the conversation history
- The coordinator tracks which agents were called for transparency
- Uses `thinking_budget: 0` for fast responses
- **No user-facing API** - only callable by other agents

## Testing

To test the coordinator, you need to call it from another agent's code:

```python
from ai_core.services import process_coordinator_message
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
result = process_coordinator_message(user, "Create a monthly budget")
print(result)
```

## Future Enhancements

- Add support for more specialized agents (Market Watcher, Planner & Forecaster, etc.)
- Implement parallel agent execution for independent tasks
- Add conversation summarization for long histories
- Implement agent performance monitoring and analytics
