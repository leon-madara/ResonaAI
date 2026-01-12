# Cultural Context Service - Quick Wins

**Goal**: Get to 80% completion in 3-5 days  
**Current**: 60% complete  
**Target**: 80% complete

---

## 🎯 High-Impact Quick Wins

### 1. Expand Knowledge Base (2-3 hours) ⚡

**Add 10 new entries** covering critical topics:

```json
{
  "id": "trauma_ptsd_east_africa",
  "content": "Trauma and PTSD in East African contexts often go unrecognized due to normalization of hardship and lack of mental health awareness. War, violence, poverty, and displacement are common but rarely discussed as sources of psychological trauma. People may present with physical symptoms (headaches, body pain) rather than emotional distress.",
  "keywords": ["trauma", "ptsd", "war", "violence", "displacement", "physical symptoms"],
  "severity": "high"
}
```

**Topics to add**:
- Trauma/PTSD
- Grief/bereavement
- Substance abuse
- Domestic violence
- Youth stress
- HIV/AIDS stigma
- Migration trauma
- Male mental health
- Postpartum depression
- Financial stress

### 2. Expand Swahili Patterns (1-2 hours) ⚡

**Add 10 new patterns**:

```json
{
  "pattern": "naomba radhi",
  "type": "excessive_apologizing",
  "severity": "medium",
  "cultural_meaning": "I apologize - excessive apologizing may indicate low self-worth, guilt, or fear of conflict",
  "probe_suggestions": [
    "I notice you're apologizing a lot. You don't need to apologize for having feelings.",
    "What makes you feel like you need to apologize right now?"
  ]
}
```

**Patterns to add**:
- naomba radhi (excessive apologizing)
- ni sawa tu (minimization)
- sitaki kuongea (withdrawal)
- sina cha kusema (shutdown)
- ni kazi tu (work stress)
- watoto wangu (parental stress)
- pesa (financial stress)
- shule (education stress)
- ndoa (marriage stress)
- familia (family pressure)

### 3. Set Up Pinecone (30 minutes) ⚡

**Steps**:
1. Go to [pinecone.io](https://www.pinecone.io) and create free account
2. Create new index:
   - Name: `cultural-context`
   - Dimensions: `384` (for sentence-transformers)
   - Metric: `cosine`
   - Region: `us-east-1`
3. Get API key from dashboard
4. Add to `.env`:
   ```bash
   PINECONE_API_KEY=your-api-key-here
   PINECONE_INDEX_NAME=cultural-context
   AUTO_INDEX_KB=true
   ```
5. Restart service - it will auto-index KB on startup

### 4. Write Integration Tests (2-3 hours) ⚡

**Create test file**: `tests/services/cultural-context/test_integration.py`

```python
"""Integration tests for cultural context service"""

async def test_cultural_context_in_conversation_flow():
    """Test cultural context integration with conversation engine"""
    # Test deflection detection
    # Test code-switching detection
    # Test voice contradiction detection
    # Test risk assessment
    pass

async def test_rag_search_performance():
    """Test vector search performance"""
    # Test search speed < 200ms
    # Test relevance scoring
    # Test language filtering
    pass
```

### 5. Update Documentation (1-2 hours) ⚡

**Create**: `docs/api/cultural-context-api.md`

```markdown
# Cultural Context API

## Endpoints

### GET /context
Get cultural context for a query

**Example**:
```bash
curl -X GET "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer token"
```

**Response**:
```json
{
  "cultural_context": [...],
  "deflection_analysis": {...},
  "code_switching_analysis": {...}
}
```
```

---

## 📋 3-Day Sprint Plan

### Day 1: Content Expansion (4-5 hours)
- ✅ Morning: Expand knowledge base (10 new entries)
- ✅ Afternoon: Expand Swahili patterns (10 new patterns)
- ✅ Evening: Set up Pinecone and test indexing

**Deliverables**:
- kb.json with 22+ entries
- swahili_patterns.json with 28+ patterns
- Production vector DB configured

### Day 2: Testing (4-5 hours)
- ✅ Morning: Write integration tests
- ✅ Afternoon: Write RAG service tests
- ✅ Evening: Write end-to-end tests

**Deliverables**:
- Integration test suite
- 90%+ test coverage
- All tests passing

### Day 3: Documentation & Polish (4-5 hours)
- ✅ Morning: Write API documentation
- ✅ Afternoon: Write integration guide
- ✅ Evening: Final testing and deployment prep

**Deliverables**:
- Complete API docs
- Integration guide
- Production-ready service

---

## 🚀 Implementation Commands

### Start Service
```bash
cd apps/backend/services/cultural-context
python main.py
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get cultural context
curl -X GET "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer test-token"

# Cultural analysis
curl -X POST "http://localhost:8000/cultural-analysis" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "I am feeling sawa", "language": "en", "emotion": "sad"}'

# Index knowledge base
curl -X POST "http://localhost:8000/index-kb?clear_existing=true" \
  -H "Authorization: Bearer test-token"
```

### Run Tests
```bash
# Run all cultural context tests
pytest tests/services/cultural-context/ -v

# Run specific test file
pytest tests/services/cultural-context/test_cultural_context.py -v

# Run with coverage
pytest tests/services/cultural-context/ --cov=apps/backend/services/cultural-context
```

---

## 📊 Progress Tracking

### Completion Checklist

**Content (40%)**:
- [ ] 10 new KB entries added
- [ ] 10 new Swahili patterns added
- [ ] Cultural norms expanded
- [ ] All entries tested

**Infrastructure (20%)**:
- [ ] Pinecone account created
- [ ] Production index configured
- [ ] Environment variables set
- [ ] Auto-indexing verified

**Testing (20%)**:
- [ ] Integration tests written
- [ ] RAG service tests written
- [ ] End-to-end tests written
- [ ] 90%+ coverage achieved

**Documentation (20%)**:
- [ ] API docs written
- [ ] Integration guide written
- [ ] Examples added
- [ ] Troubleshooting guide written

---

## 🎯 Success Metrics

### After 3 Days:
- ✅ 22+ knowledge base entries
- ✅ 28+ Swahili patterns
- ✅ Production vector DB configured
- ✅ 90%+ test coverage
- ✅ Complete API documentation
- ✅ Service at 80% completion

### Performance Targets:
- ✅ <200ms average search response time
- ✅ <500ms average API response time
- ✅ >90% pattern detection accuracy
- ✅ >85% search relevance

---

## 💡 Pro Tips

1. **Batch Operations**: Add multiple KB entries at once, then index once
2. **Test as You Go**: Test each new pattern/entry immediately
3. **Use Examples**: Base new entries on existing ones for consistency
4. **Prioritize Impact**: Focus on high-severity patterns first
5. **Document Decisions**: Note why certain patterns are high/medium/low severity

---

## 🎉 Expected Outcome

After 3 days of focused work:
- **Completion**: 60% → 80% (20% increase)
- **Production Ready**: Yes (with vector DB configured)
- **Test Coverage**: 90%+
- **Documentation**: Complete
- **Remaining Work**: Polish, optimization, additional content

**Total Time Investment**: 12-15 hours over 3 days  
**Impact**: Service moves from "infrastructure only" to "production ready"
