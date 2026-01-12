# Creating Fake User Data for UI Testing

This guide explains how to create fake user data to test the adaptive UI generation system.

## Overview

The script `create_fake_user_data.py` creates a test user with fake voice session data that simulates:
- **A stressed user** (showing anxiety, stress patterns)
- **Who enjoys fashion** (mentions fashion, shopping, style)
- **And watches drama movies on Netflix** (mentions Netflix, drama shows, entertainment as coping)

The script then:
1. Creates a test user in the database
2. Generates 10 fake voice sessions with realistic transcripts
3. Runs pattern analysis to extract user patterns
4. Triggers UI configuration generation
5. Displays the generated UI configuration

## Prerequisites

1. **Database Setup**: Ensure your PostgreSQL database is running and accessible
2. **Environment Variables**: Set `DATABASE_URL` environment variable
3. **Dependencies**: All required Python packages installed

## Usage

### Step 1: Set Database URL

Set the `DATABASE_URL` environment variable:

```bash
# Linux/Mac
export DATABASE_URL="postgresql://user:password@localhost:5432/resona_db"

# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/resona_db"

# Windows CMD
set DATABASE_URL=postgresql://user:password@localhost:5432/resona_db
```

Or update the default in the script:
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/resona_db"  # Update this
)
```

### Step 2: Run the Script

```bash
# From project root
python scripts/create_fake_user_data.py
```

**Note**: The script is currently set to print instructions. To actually run it, uncomment the `asyncio.run(main())` line at the bottom.

### Step 3: Review Output

The script will output:
- Test user ID
- Number of sessions created
- Pattern analysis results (emotions, risk level, coping strategies)
- UI configuration details (theme, components, layout)

## What Gets Created

### Test User
- A new user with `anonymous_id` like `test_user_abc12345`
- Status: `active`
- Timezone: `Africa/Nairobi`

### Voice Sessions (10 sessions)
Each session includes:
- **Transcript**: Realistic text mentioning stress, fashion, or Netflix
- **Voice Emotion**: Mostly `anxious` or `sad`, some `neutral`
- **Voice Features**: Stressed voice characteristics (higher pitch variability, faster speech, more pauses)
- **Timestamps**: Spread over the last 2 weeks

### Example Transcripts

1. **Stress + Fashion**: 
   > "I've been so stressed lately. Work is overwhelming. But I did go shopping yesterday and found this amazing dress. Fashion always helps me feel better, you know?"

2. **Stress + Netflix**:
   > "I'm feeling really anxious today. I couldn't sleep last night. I ended up watching this drama on Netflix, it was so intense. Sometimes watching shows helps me escape."

3. **Fashion Interest**:
   > "I love following fashion trends. It's one of the few things that brings me joy. I spent hours looking at fashion blogs today."

4. **Netflix Drama**:
   > "I watched this amazing drama series on Netflix last night. It was so emotional, I cried through half of it. But it felt good to feel something, you know?"

## Expected Patterns

After running pattern analysis, you should see:

### Emotional Patterns
- **Primary Emotions**: `anxious`, `sad`
- **Trajectory**: Likely `declining` or `stable`
- **Variability**: Moderate to high

### Coping Strategies
- **Effective**: `entertainment` (detected from Netflix mentions)
- **Mentioned**: Fashion-related activities, Netflix watching

### Risk Assessment
- **Risk Level**: `low` to `medium` (depending on stress indicators)
- **Factors**: Stress, anxiety patterns

### UI Configuration
The generated UI should:
- Show **stress-appropriate theme** (warm colors for depression, or calm for anxiety)
- Display **DissonanceIndicator** if word-voice gaps detected
- Show **CrisisResources** if risk is medium or higher
- Include **WhatsWorking** component showing entertainment as effective coping
- Prioritize components based on risk level

## Testing the UI

After running the script:

1. **Note the user_id** from the output
2. **Log in** to the frontend with this user (you may need to create auth credentials separately)
3. **View the interface** - it should reflect the patterns detected:
   - Theme adapted to emotional state
   - Components visible/hidden based on patterns
   - Layout prioritized by risk level

## Customization

### Modify User Profile

Edit the `transcripts` list in `create_fake_voice_sessions()` to change what the user talks about:

```python
transcripts = [
    "Your custom transcript here...",
    "Another transcript...",
    # Add more
]
```

### Change Number of Sessions

```python
session_ids = generator.create_fake_voice_sessions(user_id, num_sessions=20)  # More sessions
```

### Adjust Voice Emotions

Modify the `emotions` list to change the emotional pattern:

```python
emotions = ['happy', 'neutral', 'sad', 'anxious', ...]  # Your pattern
```

### Modify Voice Features

Change `stressed_voice_features` to simulate different voice characteristics:

```python
stressed_voice_features = {
    'prosodic': {
        'pitch_mean': 200,  # Higher pitch
        'pitch_std': 30,    # Less variability
        # ...
    },
    # ...
}
```

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Ensure database is running
- Check network connectivity

### No Patterns Found
- Ensure sessions are marked as `processed=True`
- Check that pattern analysis services are working
- Verify database schema is up to date

### UI Not Generating
- Check that patterns were successfully stored
- Verify `OvernightBuilder` is properly configured
- Check logs for error messages

## Cleanup

To remove test data:

```sql
-- Find test user
SELECT user_id, anonymous_id FROM users WHERE anonymous_id LIKE 'test_user_%';

-- Delete test user (cascades to all related data)
DELETE FROM users WHERE anonymous_id LIKE 'test_user_%';
```

## Next Steps

1. **Test Different Profiles**: Create users with different patterns (improving trajectory, different coping strategies, etc.)
2. **Test UI Changes**: Modify patterns and rebuild UI to see how it adapts
3. **Integration Testing**: Use this in automated tests to verify UI generation

## See Also

- [OVERNIGHT_BUILDER.md](../OVERNIGHT_BUILDER.md) - How UI generation works
- [PATTERN_ANALYSIS_ENGINE.md](../PATTERN_ANALYSIS_ENGINE.md) - How patterns are extracted
- [ADAPTIVE_INTERFACE_CONCEPT.md](../docs/architecture/ADAPTIVE_INTERFACE_CONCEPT.md) - UI adaptation concepts
