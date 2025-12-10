# Onboarding API Documentation (Updated)

## Overview

The onboarding system uses an AI agent to guide users through collecting their financial information. The API provides a simple conversation-style interface.

**Key Design**: 
- Check onboarding status via `/api/users/me/` 
- Use `/api/onboarding/` only for getting questions and submitting answers

---

## Flow

1. **Check Status**: Call `GET /api/users/me/` to check `profile.onboarding_status`
   - If `"not_started"` or `"in_progress"` → proceed to onboarding
   - If `"completed"` → skip to dashboard

2. **Get Question**: Call `GET /api/onboarding/`
3. **Submit Answer**: Call `POST /api/onboarding/` with answer
4. **Repeat** steps 2-3 until onboarding is complete
5. **Check Completion**: Call `GET /api/users/me/` to verify `onboarding_status === "completed"`

---

## Endpoints

### 1. GET `/api/users/me/`
**Check onboarding status and get user profile**

**Response**:
```json
{
  "id": 1,
  "username": "john_doe",
  "profile": {
    "onboarding_status": "in_progress",  // or "not_started" or "completed"
    "monthly_income": null,
    "savings": null,
    ...
  }
}
```

---

### 2. GET `/api/onboarding/`
**Get current onboarding question**

**Authentication**: Required (JWT Token)

**Response** (200 OK):
```json
{
  "question": "What is your monthly income in DZD?",
  "question_type": "direct",
  "options": null
}
```

**Question Types**:

1. **`direct`** - Free text/number input
   ```json
   {
     "question": "What is your monthly income?",
     "question_type": "direct",
     "options": null
   }
   ```

2. **`radio`** - Single choice
   ```json
   {
     "question": "What is your risk tolerance?",
     "question_type": "radio",
     "options": ["Conservative", "Moderate", "Aggressive"]
   }
   ```

3. **`checkboxes`** - Multiple choice
   ```json
   {
     "question": "Which categories are important to you?",
     "question_type": "checkboxes",
     "options": ["Groceries", "Transportation", "Entertainment"]
   }
   ```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Onboarding already completed. Check /api/users/me/ for status."
}
```

---

### 3. POST `/api/onboarding/`
**Submit answer and get next question**

**Authentication**: Required (JWT Token)

**Request Body**:

The format depends on the question type:

#### For `direct` questions:
```json
{
  "answer": "50000"
}
```

#### For `radio` questions:
```json
{
  "answer": "Moderate"
}
```

#### For `checkboxes` questions:
```json
{
  "answer": ["Groceries", "Transportation", "Healthcare"]
}
```

**Response** (200 OK) - Next Question:
```json
{
  "question": "How much do you have in savings?",
  "question_type": "direct",
  "options": null
}
```

**Response** (204 No Content) - Onboarding Complete:
When the AI agent calls `finish_onboarding_and_save_info()`, the response will be empty with status 204. Check `/api/users/me/` to confirm `onboarding_status === "completed"`.

**Error Responses**:
```json
{
  "detail": "Onboarding already completed."
}
```
```json
{
  "detail": "Onboarding not started. Call GET first."
}
```

---

### 4. POST `/api/onboarding/reset/`
**Reset onboarding status (for testing)**

**Response**:
```json
{
  "detail": "Onboarding status reset to 'not_started'."
}
```

---

## Frontend Implementation

### Recommended Flow:

```javascript
// 1. Check onboarding status
const checkStatus = async () => {
  const response = await fetch('/api/users/me/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const user = await response.json();
  
  if (user.profile.onboarding_status === 'completed') {
    navigate('/dashboard');
    return;
  }
  
  // Start onboarding
  getQuestion();
};

// 2. Get question
const getQuestion = async () => {
  const response = await fetch('/api/onboarding/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.status === 400) {
    // Onboarding complete
    navigate('/dashboard');
    return;
  }
  
  const question = await response.json();
  displayQuestion(question);
};

// 3. Display question based on type
const displayQuestion = (question) => {
  if (question.question_type === 'direct') {
    showTextInput(question.question);
  } else if (question.question_type === 'radio') {
    showRadioButtons(question.question, question.options);
  } else if (question.question_type === 'checkboxes') {
    showCheckboxes(question.question, question.options);
  }
};

// 4. Submit answer
const submitAnswer = async (answer) => {
  const response = await fetch('/api/onboarding/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ answer })
  });
  
  if (response.status === 204) {
    // Onboarding complete!
    navigate('/dashboard');
    return;
  }
  
  const nextQuestion = await response.json();
  displayQuestion(nextQuestion);
};
```

---

## Testing with cURL

### Check status:
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get question:
```bash
curl -X GET http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Submit answer (direct):
```bash
curl -X POST http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer": "50000"}'
```

### Submit answer (radio):
```bash
curl -X POST http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer": "Moderate"}'
```

### Submit answer (checkboxes):
```bash
curl -X POST http://localhost:8000/api/onboarding/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"answer": ["Groceries", "Transportation"]}'
```

---

## Summary of Changes

### Old Design (Redundant):
- GET `/api/onboarding/` → Returns status + question
- POST `/api/onboarding/` → Returns status + question
- Status was duplicated in both endpoints

### New Design (Clean):
- GET `/api/users/me/` → Check onboarding status
- GET `/api/onboarding/` → Get question only
- POST `/api/onboarding/` → Submit answer, get next question
- Status checking is centralized in `/api/users/me/`

**Benefits**:
- ✅ No redundancy
- ✅ Single source of truth for status (`/api/users/me/`)
- ✅ Cleaner API design
- ✅ Follows REST principles better
