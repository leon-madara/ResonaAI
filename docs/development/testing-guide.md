# Testing the Personalized UI System

This guide shows you how to test the complete personalized UI system that generates adaptive interfaces based on user mental health patterns.

## 🎯 What Gets Tested

1. **Pattern Analysis** - Analyzes voice sessions to detect:
   - Emotional patterns (fear, sadness, happiness, etc.)
   - Cultural context (language, code-switching, deflection phrases)
   - Triggers and coping strategies
   - Risk assessment

2. **UI Generation** - Creates personalized UI based on patterns:
   - Adaptive themes
   - Dynamic component visibility
   - Layout prioritization
   - Crisis resource prominence

3. **End-to-End Flow** - Complete system integration:
   - Backend API serves encrypted UI configs
   - Frontend fetches and displays personalized UI
   - Real-time pattern-based adaptation

## 🚀 Quick Start

### Step 1: Start the Servers

**Option A: PowerShell (Windows)**
```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
.\setup_and_run.ps1
```

**Option B: Manual Start**

Backend:
```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
$env:DATABASE_URL="postgresql://postgres:9009@localhost:5432/mental_health"
$env:JWT_SECRET_KEY="test-secret-key-dev-only"
python apps/backend/gateway/main.py
```

Frontend (in a new terminal):
```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI\apps\frontend"
$env:REACT_APP_API_URL="http://localhost:8000"
npm start
```

### Step 2: Generate Test Data

Create a test user with voice sessions and generate their personalized UI:

```powershell
cd "c:\Users\Dev Projects\ResonaAI\ResonaAI"
python scripts/create_fake_user_data.py --yes
```

This creates:
- ✅ 1 test user
- ✅ 10 fake voice sessions (stressed, interested in fashion/Netflix)
- ✅ Pattern analysis (emotions, triggers, coping strategies)
- ✅ **Personalized UI configuration** (encrypted and stored)

**Save the User ID** from the output - you'll need it!

### Step 3: Get an Auth Token

You need a JWT token to access the UI config API. Use the test user:

```powershell
# Register or login to get a token
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "consent_version": "1.0",
    "is_anonymous": false
  }'
```

The response will include an `access_token`. Copy it!

### Step 4: Test the UI Configuration

**Option A: Using the Test Page (Visual)**

1. Open http://localhost:3000/ui-test
2. Paste your JWT token
3. Click "Load UI Config"
4. See your personalized UI configuration!

**Option B: Using the API Directly**

```powershell
$token = "your_jwt_token_here"
curl -X GET http://localhost:8000/api/ui-config \
  -H "Authorization: Bearer $token"
```

## 📋 What You'll See

### 1. Theme Adaptation
Based on emotional patterns:
- **Calm theme** → For anxious/stressed users
- **Warm theme** → For users needing encouragement
- **Cool theme** → For stable emotional state

### 2. Component Visibility
Components shown/hidden based on needs:
- **CrisisResources** → Shown for high-risk users
- **CopingStrategies** → Personalized to user's effective strategies
- **EmotionalCheckIn** → Frequency based on volatility
- **CulturalGreeting** → Adapted to language preferences

### 3. Layout Prioritization
Components arranged by:
- **Risk level** → Critical items first
- **Emotional state** → Supportive content prioritized
- **Cultural context** → Language-appropriate ordering

## 🔍 Advanced Testing

### Test Different User Profiles

Modify `scripts/create_fake_user_data.py` to create users with different patterns:

```python
# Create a high-risk user
emotions = ['sad', 'hopeless', 'resigned']  # More negative emotions
transcripts = [
    "I feel hopeless...",
    "I can't go on anymore...",
    # ... crisis language
]

# Create a stable user
emotions = ['happy', 'neutral', 'surprise']
transcripts = [
    "I'm feeling good today!",
    "Things are going well...",
    # ... positive language
]
```

### Test Pattern Updates

1. Create initial data with pattern analysis
2. Add more sessions with different emotional patterns
3. Re-run pattern analysis
4. See how the UI adapts to changes

### Test Cultural Adaptation

Create sessions with Swahili phrases:

```python
transcripts = [
    "Nimechoka sana, sijui nifanye nini",  # Swahili stress
    "Habari yako? Niko sawa tu",           # Deflection phrase
    # ... mix languages
]
```

The UI will adapt to show culturally-appropriate content!

## 🎨 UI Configuration Structure

```json
{
  "theme": "calm",
  "layout": "standard",
  "components": [
    {
      "type": "EmotionalCheckIn",
      "visible": true,
      "prominence": "high",
      "props": {
        "frequency": "daily",
        "prompts": ["How are you feeling?"]
      }
    },
    {
      "type": "CrisisResources",
      "visible": true,
      "prominence": "sidebar",
      "props": {
        "risk_level": "low",
        "resources": [...]
      }
    }
  ],
  "metadata": {
    "risk_level": "low",
    "trajectory": "stable",
    "changes_count": 1
  }
}
```

## 🐛 Troubleshooting

### Backend not starting?
- Check PostgreSQL is running: `psql -U postgres -h localhost`
- Verify database exists: `mental_health`
- Check port 8000 is free: `Test-NetConnection -Port 8000`

### Frontend not loading?
- Check port 3000 is free
- Verify `node_modules` installed: `npm install`
- Check console for errors: F12 → Console

### No UI config found?
- Did you run `create_fake_user_data.py`?
- Check database: `SELECT * FROM interface_configs;`
- Verify pattern analysis ran: `SELECT * FROM user_patterns;`

### Authentication errors?
- Token might be expired (24h expiration)
- Re-login to get a fresh token
- Check token format: Should be a long JWT string

## 📊 Verify Pattern Analysis

Check what patterns were detected:

```sql
-- View user patterns
SELECT 
    user_id,
    primary_emotions,
    risk_level,
    trajectory,
    generated_at
FROM user_patterns
WHERE is_current = true;

-- View UI configs
SELECT 
    user_id,
    version,
    theme,
    primary_components,
    crisis_prominence,
    generated_at
FROM interface_configs
WHERE is_current = true;
```

## 🎯 Success Criteria

You've successfully tested the system when:
- ✅ Backend API returns UI config for authenticated users
- ✅ Frontend displays personalized theme and components
- ✅ Different user patterns result in different UIs
- ✅ Cultural context adapts the interface appropriately
- ✅ Risk levels affect component visibility and prominence

## 📚 Next Steps

1. **Test with Real Voice Sessions** - Replace fake data with actual voice recordings
2. **Implement Decryption** - Add proper Web Crypto API integration
3. **Test Offline Mode** - Verify UI config caching works offline
4. **Test UI Updates** - See real-time UI adaptation as patterns change
5. **Test Multiple Users** - Create different profiles and compare UIs

## 🔗 Related Documentation

- [PATTERN_ANALYSIS_ENGINE.md](PATTERN_ANALYSIS_ENGINE.md) - How patterns are detected
- [OVERNIGHT_BUILDER.md](OVERNIGHT_BUILDER.md) - How UI is generated
- [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) - Frontend structure
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database schema

---

**Need Help?** Check the logs:
- Backend: Terminal running `python apps/backend/gateway/main.py`
- Frontend: Terminal running `npm start`
- Database: `tail -f /var/log/postgresql/postgresql.log`
