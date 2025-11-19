# Users API Documentation

## Endpoints

### 1. POST `/api/users/create/`
Create a new user account and receive JWT tokens.

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Username already exists."
}
```

---

### 2. GET `/api/users/me/`
Get the current authenticated user's profile with all financial data.

**Authentication**: Required (JWT Token)

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "onboarding_status": "completed",
    "monthly_income": "50000.00",
    "savings": "100000.00",
    "investments": "25000.00",
    "debts": "15000.00",
    "user_ai_preferences": {
      "risk_preference": "moderate",
      "tone": "friendly",
      "style": "conversational"
    },
    "personal_info": {
      "preferred_currency": "DZD",
      "location_context": "Algeria"
    },
    "extra_info": {
      "goals": ["Save for house", "Pay off debt"],
      "budget_categories": ["Groceries", "Transportation", "Healthcare"]
    },
    "ai_summary": "User is a moderate risk investor focused on saving for a house while managing existing debt."
  }
}
```

---

## Testing with cURL

### Create a new user:
```bash
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Get current user profile:
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Authentication Flow

1. **Create user** → Receive `access` and `refresh` tokens
2. **Use access token** in `Authorization: Bearer <token>` header for all authenticated requests
3. **Refresh token** when access token expires using `/api/token/refresh/`

### Refresh Token Example:
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

Response:
```json
{
  "access": "NEW_ACCESS_TOKEN"
}
```

---

## UserProfile Fields

| Field | Type | Description | Editable |
|-------|------|-------------|----------|
| `onboarding_status` | string | Status: not_started, in_progress, completed | No (read-only) |
| `monthly_income` | decimal | Monthly income amount | Yes |
| `savings` | decimal | Current savings amount | Yes |
| `investments` | decimal | Current investment holdings | Yes |
| `debts` | decimal | Current debt amount | Yes |
| `user_ai_preferences` | JSON | AI behavior preferences (tone, style, risk) | Yes |
| `personal_info` | JSON | Personal information (currency, location) | Yes |
| `extra_info` | JSON | Additional info (goals, categories, habits) | Yes |
| `ai_summary` | text | AI-generated profile summary | No (read-only) |

---

## Notes

- All decimal fields support up to 10 digits with 2 decimal places
- `onboarding_status` and `ai_summary` are read-only (set by the system)
- JSON fields can contain any valid JSON structure
- Profile is automatically created when user is created
