# Onboarding Agent Integration - Complete

## ✅ What Was Implemented

### 1. **Tools** (`onboarding/tools.py`)
Cleaned up and properly structured the agent tools:

#### `ask_question(question, question_type, options)`
- Returns structured question data
- Validates that options are provided for radio/checkboxes
- Validates that options are NOT provided for direct questions
- Returns dict matching the serializer format

#### `finish_onboarding_and_save_info(...)`
- Saves all collected data to UserProfile
- Sets `onboarding_status = 'completed'`
- Fixed parameter name: `monthly_income` (was `mounthly_income`)

### 2. **Agent Service** (`onboarding/services.py`)
Created a complete service layer for the onboarding agent:

#### `get_or_create_onboarding_agent()`
- Creates/retrieves the onboarding agent from database
- Registers both functions with the agent
- Uses the agent service layer from `agents.services`

#### `process_onboarding_turn(user, user_message)`
- Handles one complete conversation turn
- Gets conversation history
- Calls Gemini API with agent config
- Executes function calls (ask_question or finish_onboarding)
- Returns structured response:
  - `{"type": "question", "data": {...}}`
  - `{"type": "completed", "data": {...}}`
  - `{"type": "error", "data": {...}}`

### 3. **Views Updated** (`onboarding/views.py`)
Integrated the AI agent into both endpoints:

#### GET `/api/onboarding/`
- Calls `process_onboarding_turn(user, None)` to get first question
- Returns question data from AI agent
- Handles errors gracefully

#### POST `/api/onboarding/`
- Converts user answer to string
- Calls `process_onboarding_turn(user, answer)`
- Returns next question or 204 No Content if completed
- Handles errors gracefully

---

## 🔧 How It Works

### Flow Diagram:

```
User → GET /api/onboarding/
  ↓
Views → process_onboarding_turn(user, None)
  ↓
Service → Get agent, build config, call Gemini
  ↓
Gemini → Calls ask_question(...)
  ↓
Service → Executes ask_question function
  ↓
Views → Returns question to user
  ↓
User → Sees question, submits answer
  ↓
User → POST /api/onboarding/ with answer
  ↓
Views → process_onboarding_turn(user, answer)
  ↓
Service → Send answer to Gemini
  ↓
Gemini → Either:
  - Calls ask_question(...) → Next question
  - Calls finish_onboarding_and_save_info(...) → Complete
  ↓
Service → Executes function
  ↓
Views → Returns next question OR 204 No Content
```

---

## 📋 Agent Configuration

**Model**: `gemini-2.0-flash-exp`  
**Thinking Budget**: 1000  
**System Instruction**: Detailed onboarding persona (see `services.py`)

**Required Data to Collect**:
1. Monthly Income (float)
2. Savings (float)
3. Investments (float)
4. Debts (float)
5. User AI Preferences (dict: risk_preference, tone, style)
6. Personal Info (dict: preferred_currency, location_context)
7. Extra Info (dict: goals, budget_categories, habits, etc.)
8. AI Summary (string: 2-4 sentences)

---

## 🧪 Testing

### 1. Create a user and get token:
```bash
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 2. Start onboarding (GET first question):
```bash
curl -X GET http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "question": "Welcome! Let's get started...",
  "question_type": "direct",
  "options": null
}
```

### 3. Submit answer:
```bash
curl -X POST http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer": "50000"}'
```

### 4. Continue until completion:
When onboarding is complete, you'll get:
```
HTTP 204 No Content
```

### 5. Verify completion:
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Check that `profile.onboarding_status === "completed"`

---

## 🔍 Debugging

### Check conversation history:
The agent stores all conversation in the `ConversationHistory` model.

### Check agent registration:
```python
from agents.models import agentModel
from agents.services import get_agent_functions

agent = agentModel.objects.get(name="onboarding_agent")
functions = get_agent_functions(agent.id)
print(functions.keys())  # Should show: ['ask_question', 'finish_onboarding_and_save_info']
```

### Check if agent was created:
```python
from onboarding.services import get_or_create_onboarding_agent

agent = get_or_create_onboarding_agent()
print(agent.name, agent.gemini_model)
```

---

## 🚨 Common Issues

### 1. "GENAI_API_KEY not found"
Make sure your `.env` file has:
```
GENAI_API_KEY=your_api_key_here
```

### 2. Agent doesn't call functions
Check that:
- Functions are registered: `get_agent_functions(agent.id)`
- Function declarations are valid JSON
- System instruction is clear about when to call functions

### 3. Conversation history issues
Reset conversation:
```python
from agents.models import ConversationHistory
from django.contrib.auth.models import User

user = User.objects.get(username="testuser")
ConversationHistory.objects.filter(user=user).delete()
```

---

## 📁 Files Created/Modified

### Created:
- `onboarding/services.py` - Agent service layer
- `onboarding/tools.py` - Cleaned up tools

### Modified:
- `onboarding/views.py` - Integrated AI agent
- `onboarding/agent.py` - (existing, not modified)

---

## ✨ Next Steps

The onboarding agent is now fully functional! You can:

1. **Test it** with real users
2. **Customize the system instruction** to change agent behavior
3. **Add more validation** to the tools if needed
4. **Monitor conversation history** to improve questions
5. **Adjust thinking budget** if responses are too slow/fast

The agent will now:
- ✅ Ask questions one at a time
- ✅ Collect all required financial data
- ✅ Save data to UserProfile when complete
- ✅ Handle errors gracefully
- ✅ Maintain conversation context
