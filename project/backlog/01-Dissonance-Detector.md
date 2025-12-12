# To Do: Dissonance Detector

## Status: ❌ NOT IMPLEMENTED (0%)

**Last Updated**: December 12, 2025  
**Priority**: ⭐⭐⭐⭐⭐ CRITICAL - This is THE core innovation  
**Estimated Effort**: 2-3 weeks  
**Lines of Code**: ~600-800 lines

---

## Overview

**THE CORE INNOVATION** - Compare what users SAY (transcript sentiment) vs how they SOUND (voice emotion) to detect hidden distress. This is the feature that differentiates ResonaAI from other emotion classifiers.

**Key Innovation**: Detects truth gaps like "I'm fine" said with a sad voice, revealing concealed emotional states.

---

## Why This Is Critical

### Business Impact
- **Differentiator**: This is ResonaAI's unique value proposition
- **Market Position**: No other platform detects voice-text dissonance
- **User Value**: Catches cases where users say they're okay but aren't

### Technical Impact
- **Core Feature**: Required for risk assessment
- **Foundation**: Other services depend on this
- **Blocking**: Risk Assessment cannot be built without this

### Safety Impact
- **Crisis Prevention**: Detects concealed distress
- **Early Intervention**: Catches problems before they escalate
- **Lifesaving**: Can detect suicide risk indicators

---

## What's Missing

### Service Directory
**Status**: Completely missing

```
services/dissonance-detector/     ❌ DOES NOT EXIST
├── __init__.py                   ❌
├── main.py                       ❌
├── config.py                     ❌
├── Dockerfile                    ❌
├── requirements.txt              ❌
├── models/
│   └── dissonance_models.py     ❌
└── services/
    ├── sentiment_analyzer.py    ❌
    └── dissonance_calculator.py  ❌
```

### API Gateway Route
**Status**: Not configured

**Needed**:
- ❌ Route in API Gateway: `POST /dissonance/analyze`
- ❌ Service URL configuration
- ❌ Request forwarding logic

### Docker Compose Configuration
**Status**: Not configured

**Needed**:
- ❌ Service definition in docker-compose.yml
- ❌ Port mapping
- ❌ Environment variables
- ❌ Dependencies

---

## Required Implementation

### 1. Service Structure

#### Main Application (`main.py`)
**File**: `services/dissonance-detector/main.py`  
**Status**: Not created

**Required Endpoints**:
```python
# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dissonance-detector"}

# Main analysis endpoint
@app.post("/analyze")
async def analyze_dissonance(
    request: DissonanceRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> DissonanceResponse:
    """
    Analyze dissonance between transcript sentiment and voice emotion
    
    Request:
    {
        "transcript": "I'm fine, everything is okay",
        "voice_emotion": {
            "emotion": "sad",
            "confidence": 0.85
        },
        "session_id": "uuid",
        "user_id": "uuid"
    }
    
    Response:
    {
        "dissonance_level": "high",
        "dissonance_score": 0.82,
        "stated_emotion": "positive",
        "actual_emotion": "negative",
        "interpretation": "defensive_concealment",
        "risk_level": "medium-high",
        "confidence": 0.82,
        "details": {
            "sentiment_score": 0.75,
            "emotion_score": -0.65,
            "gap": 1.40
        }
    }
    """
```

**Required Features**:
- ✅ FastAPI application setup
- ✅ Authentication middleware integration
- ✅ Request validation
- ✅ Error handling
- ✅ Logging
- ✅ Response formatting

#### Configuration (`config.py`)
**File**: `services/dissonance-detector/config.py`  
**Status**: Not created

**Required Settings**:
```python
class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "dissonance-detector"
    SERVICE_PORT: int = 8000
    
    # Sentiment Analysis
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    SENTIMENT_CACHE_SIZE: int = 1000
    
    # Dissonance Calculation
    DISSONANCE_THRESHOLDS: Dict[str, float] = {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7
    }
    
    # Emotion Mapping
    EMOTION_VALENCE_MAP: Dict[str, float] = {
        "happy": 0.8,
        "neutral": 0.0,
        "sad": -0.7,
        "angry": -0.6,
        "fear": -0.8,
        "surprise": 0.3,
        "disgust": -0.5
    }
    
    # Risk Mapping
    RISK_MAPPING: Dict[str, str] = {
        "low": "low",
        "medium": "medium",
        "high": "medium-high",
        "critical": "high"
    }
    
    # Dependencies
    EMOTION_SERVICE_URL: str = "http://emotion-analysis:8000"
    DATABASE_URL: str
    REDIS_URL: str
    
    class Config:
        env_file = ".env"
```

#### Data Models (`models/dissonance_models.py`)
**File**: `services/dissonance-detector/models/dissonance_models.py`  
**Status**: Not created

**Required Models**:
```python
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class DissonanceRequest(BaseModel):
    transcript: str = Field(..., description="User's spoken transcript")
    voice_emotion: Dict[str, Any] = Field(..., description="Voice emotion from emotion detector")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class SentimentResult(BaseModel):
    label: str  # positive, negative, neutral
    score: float  # 0-1 confidence
    valence: float  # -1 to 1 (negative to positive)

class DissonanceDetails(BaseModel):
    sentiment_score: float  # -1 to 1
    emotion_score: float  # -1 to 1
    gap: float  # absolute difference
    normalized_gap: float  # 0 to 1

class DissonanceResponse(BaseModel):
    dissonance_level: str  # low, medium, high, critical
    dissonance_score: float  # 0 to 1
    stated_emotion: str  # positive, negative, neutral
    actual_emotion: str  # positive, negative, neutral
    interpretation: str  # defensive_concealment, authentic, etc.
    risk_level: str  # low, medium, medium-high, high
    confidence: float  # 0 to 1
    details: DissonanceDetails
    timestamp: datetime
```

### 2. Sentiment Analyzer

#### Implementation (`services/sentiment_analyzer.py`)
**File**: `services/dissonance-detector/services/sentiment_analyzer.py`  
**Status**: Not created

**Required Functionality**:
```python
from transformers import pipeline
from typing import Dict
import logging

class SentimentAnalyzer:
    """Analyze sentiment from transcript text"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.sentiment_pipeline = None
        self.cache = {}  # Simple cache for performance
        
    async def load_model(self):
        """Load sentiment analysis model"""
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                return_all_scores=True
            )
            logging.info(f"Sentiment model loaded: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to load sentiment model: {e}")
            raise
    
    async def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Returns:
        {
            "label": "positive",  # or "negative", "neutral"
            "score": 0.85,
            "valence": 0.75  # -1 to 1
        }
        """
        # Check cache
        if text in self.cache:
            return self.cache[text]
        
        # Analyze
        results = self.sentiment_pipeline(text)
        
        # Extract best result
        best_result = max(results[0], key=lambda x: x['score'])
        
        # Map to valence (-1 to 1)
        label = best_result['label'].lower()
        if 'positive' in label:
            valence = best_result['score']
        elif 'negative' in label:
            valence = -best_result['score']
        else:  # neutral
            valence = 0.0
        
        result = {
            "label": label,
            "score": best_result['score'],
            "valence": valence
        }
        
        # Cache result
        if len(self.cache) < 1000:
            self.cache[text] = result
        
        return result
```

**Required Features**:
- ✅ Transformers pipeline integration
- ✅ Sentiment label extraction (positive/negative/neutral)
- ✅ Confidence scoring
- ✅ Valence mapping (-1 to 1 scale)
- ✅ Caching for performance
- ✅ Error handling

**Model Options**:
1. **cardiffnlp/twitter-roberta-base-sentiment-latest** (Recommended)
   - Fast, accurate
   - Good for conversational text
   - Supports positive/negative/neutral

2. **distilbert-base-uncased-finetuned-sst-2-english**
   - Smaller, faster
   - Binary classification only

3. **nlptown/bert-base-multilingual-uncased-sentiment**
   - Multilingual support
   - Good for Swahili/English code-switching

### 3. Dissonance Calculator

#### Implementation (`services/dissonance_calculator.py`)
**File**: `services/dissonance-detector/services/dissonance_calculator.py`  
**Status**: Not created

**Required Functionality**:
```python
from typing import Dict, Any
import logging

class DissonanceCalculator:
    """Calculate dissonance between stated and actual emotion"""
    
    def __init__(self, emotion_valence_map: Dict[str, float], thresholds: Dict[str, float]):
        self.emotion_valence_map = emotion_valence_map
        self.thresholds = thresholds
    
    def calculate(
        self,
        sentiment_result: Dict,
        voice_emotion: Dict[str, Any]
    ) -> Dict:
        """
        Calculate dissonance between sentiment and voice emotion
        
        Returns:
        {
            "dissonance_level": "high",
            "dissonance_score": 0.82,
            "stated_emotion": "positive",
            "actual_emotion": "negative",
            "interpretation": "defensive_concealment",
            "risk_level": "medium-high",
            "confidence": 0.82,
            "details": {
                "sentiment_score": 0.75,
                "emotion_score": -0.65,
                "gap": 1.40,
                "normalized_gap": 0.70
            }
        }
        """
        # Extract sentiment valence
        sentiment_valence = sentiment_result['valence']
        
        # Extract emotion valence
        emotion_name = voice_emotion.get('emotion', 'neutral')
        emotion_confidence = voice_emotion.get('confidence', 0.5)
        emotion_valence = self.emotion_valence_map.get(emotion_name, 0.0)
        
        # Weight emotion by confidence
        weighted_emotion_valence = emotion_valence * emotion_confidence
        
        # Calculate gap
        gap = abs(sentiment_valence - weighted_emotion_valence)
        
        # Normalize gap (0 to 1 scale)
        # Max gap is 2.0 (sentiment +1, emotion -1)
        normalized_gap = gap / 2.0
        
        # Determine dissonance level
        dissonance_level = self._get_dissonance_level(normalized_gap)
        
        # Determine interpretation
        interpretation = self._get_interpretation(
            sentiment_valence,
            weighted_emotion_valence,
            dissonance_level
        )
        
        # Map to risk level
        risk_level = self._map_to_risk(dissonance_level, interpretation)
        
        # Calculate overall confidence
        confidence = min(sentiment_result['score'], emotion_confidence)
        
        return {
            "dissonance_level": dissonance_level,
            "dissonance_score": normalized_gap,
            "stated_emotion": self._get_emotion_label(sentiment_valence),
            "actual_emotion": self._get_emotion_label(weighted_emotion_valence),
            "interpretation": interpretation,
            "risk_level": risk_level,
            "confidence": confidence,
            "details": {
                "sentiment_score": sentiment_valence,
                "emotion_score": weighted_emotion_valence,
                "gap": gap,
                "normalized_gap": normalized_gap
            }
        }
    
    def _get_dissonance_level(self, normalized_gap: float) -> str:
        """Get dissonance level from normalized gap"""
        if normalized_gap >= self.thresholds['high']:
            return "high"
        elif normalized_gap >= self.thresholds['medium']:
            return "medium"
        else:
            return "low"
    
    def _get_interpretation(
        self,
        sentiment_valence: float,
        emotion_valence: float,
        dissonance_level: str
    ) -> str:
        """Interpret the dissonance pattern"""
        if dissonance_level == "low":
            return "authentic"
        
        # Positive sentiment, negative emotion = defensive concealment
        if sentiment_valence > 0.3 and emotion_valence < -0.3:
            return "defensive_concealment"
        
        # Negative sentiment, positive emotion = recovery/improvement
        if sentiment_valence < -0.3 and emotion_valence > 0.3:
            return "recovery_indicator"
        
        # Both negative but different intensities
        if sentiment_valence < 0 and emotion_valence < 0:
            return "intensity_mismatch"
        
        return "unclear"
    
    def _get_emotion_label(self, valence: float) -> str:
        """Get emotion label from valence"""
        if valence > 0.3:
            return "positive"
        elif valence < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _map_to_risk(self, dissonance_level: str, interpretation: str) -> str:
        """Map dissonance to risk level"""
        if dissonance_level == "high" and interpretation == "defensive_concealment":
            return "medium-high"
        elif dissonance_level == "high":
            return "medium"
        elif dissonance_level == "medium":
            return "low"
        else:
            return "low"
```

**Required Features**:
- ✅ Valence extraction from sentiment
- ✅ Valence extraction from emotion
- ✅ Gap calculation
- ✅ Normalization (0 to 1 scale)
- ✅ Dissonance level classification
- ✅ Interpretation generation
- ✅ Risk level mapping
- ✅ Confidence calculation

---

## Integration Points

### Dependencies

#### ✅ Available Services
- ✅ **Speech Processing Service** (`services/speech-processing/`)
  - Provides transcript
  - Endpoint: `POST /transcribe`
  - Returns: `{transcript: str, ...}`

- ✅ **Emotion Detector** (`src/emotion_detector.py`)
  - Provides voice emotion
  - Method: `detect_emotion(audio)`
  - Returns: `EmotionResult(emotion, confidence, ...)`

#### ❌ Missing Services
- ❌ **API Gateway Route** - Need to add route
- ❌ **Docker Compose Config** - Need to add service

### Integration Flow

**Current Flow** (without Dissonance Detector):
```
User speaks → Speech Processing → Transcript
                ↓
            Emotion Detector → Voice Emotion
                ↓
            (No dissonance analysis)
```

**Target Flow** (with Dissonance Detector):
```
User speaks → Speech Processing → Transcript
                ↓
            Emotion Detector → Voice Emotion
                ↓
            Dissonance Detector → Dissonance Analysis
                ↓
            Risk Assessment → Risk Score
```

### API Integration

**Input Sources**:
1. **Transcript** - From Speech Processing Service
   - Endpoint: `POST /api/speech/transcribe`
   - Response: `{transcript: "I'm fine", ...}`

2. **Voice Emotion** - From Emotion Detector
   - Endpoint: `POST /api/emotion/analyze`
   - Response: `{emotion: "sad", confidence: 0.85, ...}`

**Output Consumers**:
1. **Risk Assessment Service** - Uses dissonance for risk calculation
2. **Conversation Engine** - Uses dissonance for response adaptation
3. **Cultural Context Service** - Uses dissonance for cultural pattern detection

---

## Implementation Plan

### Phase 1: Service Setup (Days 1-2)
**Estimated**: 2 days

**Tasks**:
- [ ] Create `services/dissonance-detector/` directory
- [ ] Create `main.py` with FastAPI app
- [ ] Create `config.py` with settings
- [ ] Create `Dockerfile`
- [ ] Create `requirements.txt`
- [ ] Create `models/dissonance_models.py`
- [ ] Create directory structure
- [ ] Add health check endpoint
- [ ] Test service starts

**Deliverable**: Service skeleton that responds to health check

### Phase 2: Sentiment Analysis (Days 3-5)
**Estimated**: 3 days

**Tasks**:
- [ ] Install transformers library
- [ ] Create `services/sentiment_analyzer.py`
- [ ] Implement model loading
- [ ] Implement sentiment analysis
- [ ] Implement valence mapping
- [ ] Add caching
- [ ] Write unit tests
- [ ] Test with sample transcripts

**Deliverable**: Working sentiment analyzer

**Test Cases**:
- "I'm fine" → positive sentiment
- "I'm not okay" → negative sentiment
- "Everything is great" → positive sentiment
- "I'm struggling" → negative sentiment

### Phase 3: Dissonance Calculation (Days 6-8)
**Estimated**: 3 days

**Tasks**:
- [ ] Create `services/dissonance_calculator.py`
- [ ] Implement valence extraction
- [ ] Implement gap calculation
- [ ] Implement dissonance level classification
- [ ] Implement interpretation generation
- [ ] Implement risk mapping
- [ ] Write unit tests
- [ ] Test with "I'm fine" + sad voice scenario

**Deliverable**: Working dissonance calculator

**Test Cases**:
- "I'm fine" + sad voice → high dissonance
- "I'm fine" + happy voice → low dissonance
- "I'm sad" + sad voice → low dissonance
- "I'm okay" + neutral voice → low dissonance

### Phase 4: Integration (Days 9-10)
**Estimated**: 2 days

**Tasks**:
- [ ] Integrate sentiment analyzer
- [ ] Integrate dissonance calculator
- [ ] Create main analysis endpoint
- [ ] Add API Gateway route
- [ ] Add Docker Compose configuration
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Documentation

**Deliverable**: Fully integrated service

### Phase 5: Testing & Validation (Days 11-15)
**Estimated**: 5 days

**Tasks**:
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] Accuracy validation (target: 80%+)
- [ ] Performance testing
- [ ] Edge case testing
- [ ] Error handling testing
- [ ] Documentation

**Deliverable**: Validated and tested service

---

## Dependencies

### Python Libraries
**File**: `services/dissonance-detector/requirements.txt`

**Required**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
transformers==4.36.0
torch==2.1.1
numpy==1.24.3
redis==5.0.1
sqlalchemy==2.0.23
python-dotenv==1.0.0
```

### External Services
- ✅ Speech Processing Service (available)
- ✅ Emotion Detector (available)
- ✅ PostgreSQL (available)
- ✅ Redis (available)

### Internal Services
- ❌ API Gateway route (needs to be added)
- ❌ Docker Compose config (needs to be added)

---

## Success Criteria

### Functional Requirements
- ✅ Catches 80%+ of "I'm fine" + sad voice cases
- ✅ Service deployed and functional
- ✅ Integrated with emotion_detector.py
- ✅ API endpoint available
- ✅ Unit tests passing
- ✅ Integration tests passing

### Performance Requirements
- ✅ Response time < 500ms (95th percentile)
- ✅ Can handle 100 requests/second
- ✅ Model loading time < 5 seconds
- ✅ Memory usage < 2GB

### Accuracy Requirements
- ✅ Dissonance detection accuracy: 80%+
- ✅ False positive rate: < 10%
- ✅ False negative rate: < 5%

### Quality Requirements
- ✅ Code coverage: 80%+
- ✅ Documentation complete
- ✅ Error handling comprehensive
- ✅ Logging comprehensive

---

## Example Use Cases

### Use Case 1: "I'm Fine" with Sad Voice
**Input**:
```json
{
  "transcript": "I'm fine, everything is okay",
  "voice_emotion": {
    "emotion": "sad",
    "confidence": 0.85
  }
}
```

**Expected Output**:
```json
{
  "dissonance_level": "high",
  "dissonance_score": 0.82,
  "stated_emotion": "positive",
  "actual_emotion": "negative",
  "interpretation": "defensive_concealment",
  "risk_level": "medium-high",
  "confidence": 0.82
}
```

### Use Case 2: "I'm Sad" with Sad Voice
**Input**:
```json
{
  "transcript": "I'm feeling really sad today",
  "voice_emotion": {
    "emotion": "sad",
    "confidence": 0.90
  }
}
```

**Expected Output**:
```json
{
  "dissonance_level": "low",
  "dissonance_score": 0.15,
  "stated_emotion": "negative",
  "actual_emotion": "negative",
  "interpretation": "authentic",
  "risk_level": "low",
  "confidence": 0.90
}
```

### Use Case 3: "I'm Okay" with Neutral Voice
**Input**:
```json
{
  "transcript": "I'm okay, nothing special",
  "voice_emotion": {
    "emotion": "neutral",
    "confidence": 0.70
  }
}
```

**Expected Output**:
```json
{
  "dissonance_level": "low",
  "dissonance_score": 0.20,
  "stated_emotion": "neutral",
  "actual_emotion": "neutral",
  "interpretation": "authentic",
  "risk_level": "low",
  "confidence": 0.70
}
```

---

## Blockers

### Current Blockers
1. **No service implementation** - Directory doesn't exist
2. **No sentiment analysis** - Need transformers integration
3. **No API Gateway route** - Need to add route
4. **No Docker Compose config** - Need to add service

### Dependencies
- ✅ Speech Processing Service (available)
- ✅ Emotion Detector (available)
- ❌ API Gateway route (needs to be added)
- ❌ Docker Compose config (needs to be added)

**No Blocking Dependencies**: Can start implementation immediately

---

## Timeline

**Total Effort**: 2-3 weeks  
**Team**: 1 backend engineer  
**Lines of Code**: ~600-800 lines  
**Complexity**: Medium (NLP integration, mathematical calculations)

**Timeline**: Weeks 1-3 (Priority 1 - Build FIRST)

---

## Next Immediate Steps

1. **Create Service Directory** (30 minutes)
   ```bash
   mkdir -p services/dissonance-detector/{models,services}
   ```

2. **Create Basic FastAPI App** (2 hours)
   - `main.py` with health check
   - `config.py` with settings
   - `Dockerfile`
   - `requirements.txt`

3. **Implement Sentiment Analyzer** (3 days)
   - Install transformers
   - Implement sentiment analysis
   - Test with sample text

4. **Implement Dissonance Calculator** (3 days)
   - Implement gap calculation
   - Implement classification
   - Test with "I'm fine" scenario

5. **Integration** (2 days)
   - Add API Gateway route
   - Add Docker Compose config
   - End-to-end testing

---

## References

- **Design Spec**: `DESIGN_CRITIQUE_AND_IMPROVEMENTS.md` - Gap 1
- **Architecture**: `architecture/system-design.md` lines 79-95
- **Progress Report**: `PROGRESS_REPORT.md` - Gap 1
- **Missing Components**: `MISSING_COMPONENTS_REPORT.md` - Component 1
- **Emotion Detector**: `src/emotion_detector.py` (for voice emotion integration)
