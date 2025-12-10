# Agent Function Registration Examples

This document shows how to register the `send_message_to_agent` function for different agents with their specific allowed agents.

## Main AI Coordinator

The Main AI Coordinator can call ALL agents (except onboarding):

```python
from agents.services import register_agent_function
from ai_core.tools import send_message_to_agent, send_message_to_agent_declaration

register_agent_function(
    agent_id=agent.id,
    func_name="send_message_to_agent",
    function_declaration=send_message_to_agent_declaration,  # Has all agents
    function=send_message_to_agent
)
```

## Chatbot Agent

The Chatbot might need to call the coordinator and maybe the notification agent:

```python
from agents.services import register_agent_function
from ai_core.tools import (
    send_message_to_agent, 
    create_send_message_declaration,
    call_main_coordinator,
    call_main_coordinator_declaration
)

# Register coordinator call
register_agent_function(
    agent_id=agent.id,
    func_name="call_main_coordinator",
    function_declaration=call_main_coordinator_declaration,
    function=call_main_coordinator
)

# Or use send_message_to_agent with limited agents
chatbot_send_message_declaration = create_send_message_declaration([
    "main_ai_coordinator",
    "notification_agent"
])

register_agent_function(
    agent_id=agent.id,
    func_name="send_message_to_agent",
    function_declaration=chatbot_send_message_declaration,
    function=send_message_to_agent
)
```

## Budget Agent

The Budget Agent might only need to call the notification agent:

```python
from agents.services import register_agent_function
from ai_core.tools import send_message_to_agent, create_send_message_declaration

budget_send_message_declaration = create_send_message_declaration([
    "notification_agent"
])

register_agent_function(
    agent_id=agent.id,
    func_name="send_message_to_agent",
    function_declaration=budget_send_message_declaration,
    function=send_message_to_agent
)
```

## Forecast Agent

The Forecast Agent might need budget and market data:

```python
from agents.services import register_agent_function
from ai_core.tools import send_message_to_agent, create_send_message_declaration

forecast_send_message_declaration = create_send_message_declaration([
    "budget_agent",
    "market_watcher",
    "notification_agent"
])

register_agent_function(
    agent_id=agent.id,
    func_name="send_message_to_agent",
    function_declaration=forecast_send_message_declaration,
    function=send_message_to_agent
)
```

## Key Points

1. **All agents use the SAME `send_message_to_agent` function** - it routes to all agents
2. **Each agent gets a CUSTOM declaration** with only the agents it should call
3. **Use `create_send_message_declaration(allowed_agents)`** to create custom declarations
4. **The Gemini model will only see the agents in its declaration** - this prevents unauthorized calls

## Available Agents

- `budget_agent` - Budget generation and management
- `chatbot_agent` - General conversation
- `main_ai_coordinator` - Central orchestrator
- `market_watcher` - Market analysis (not yet implemented)
- `receipt_parser` - Receipt parsing (not yet implemented)
- `product_advisor` - Product recommendations
- `notification_agent` - Notifications and alerts
- `expense_manager` - Expense tracking (not yet implemented)
- `forecast_agent` - Financial forecasting

**Note**: `onboarding_agent` is NOT in the list - it should never be called by other agents.
