# 🚀 START HERE: Cultural Context Service Implementation

**Goal**: Get Cultural Context Service from 60% to 100% completion  
**Timeline**: 1-2 weeks  
**Start Date**: Today

---

## 📋 Today's Tasks (Day 1) - 4-5 hours

### Task 1: Expand Knowledge Base (2-3 hours) ⚡

**File**: `apps/backend/services/cultural-context/data/kb.json`

**Add 10 new entries** covering these critical topics:

1. **Trauma/PTSD** - War, violence, displacement trauma
2. **Grief/Bereavement** - Cultural mourning practices
3. **Substance Abuse** - Alcohol, khat, stigma
4. **Domestic Violence** - Cultural barriers to reporting
5. **Youth Mental Health** - Education pressure, identity
6. **HIV/AIDS Stigma** - Mental health impact
7. **Migration Trauma** - Displacement, refugee experience
8. **Male Mental Health** - Masculinity, emotional expression
9. **Postpartum Depression** - Cultural views on motherhood
10. **Financial Stress** - Poverty, unemployment, family obligations

**Template to use**:
```json
{
  "id": "unique_id_here",
  "content": "Detailed cultural context explanation (2-3 sentences)",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "language": "en",
  "region": "east_africa",
  "category": "category_name",
  "severity": "low|medium|high",
  "cultural_significance": "low|medium|high|very_high"
}
```

**Example**:
```json
{
  "id": "trauma_ptsd_east_africa",
  "content": "Trauma and PTSD in East African contexts often go unrecognized due to normalization of hardship and lack of mental health awareness. War, violence, poverty, and displacement are common but rarely discussed as sources of psychological trauma. People may present with physical symptoms (headaches, body pain) rather than emotional distress, as somatic complaints are more culturally acceptable.",
  "keywords": ["trauma", "ptsd", "war", "violence", "displacement", "physical symptoms", "somatic", "hardship"],
  "language": "en",
  "region": "east_africa",
  "category": "trauma_disorders",
  "severity": "high",
  "cultural_significance": "very_high"
}
```

### Task 2: Expand Swahili Patterns (1-2 hours) ⚡

**File**: `apps/backend/services/cultural-context/data/swahili_patterns.json`

**Add 10 new patterns** to the `patterns` array:

1. **naomba radhi** - Excessive apologizing
2. **ni sawa tu** - Minimization ("it's just okay")
3. **sitaki kuongea** - Withdrawal ("I don't want to talk")
4. **sina cha kusema** - Shutdown ("I have nothing to say")
5. **ni kazi tu** - Work stress deflection
6. **watoto wangu** - Parental stress/burden
7. **pesa** - Financial stress
8. **shule** - Education stress
9. **ndoa** - Marriage/relationship stress
10. **familia** - Family pressure

**Template to use**:
```json
{
  "pattern": "swahili_phrase",
  "type": "pattern_type",
  "severity": "low|medium|high",
  "cultural_meaning": "Cultural interpretation (1-2 sentences)",
  "interpretation": "What this means for mental health (1-2 sentences)",
  "probe_suggestions": [
    "Empathetic probe question 1",
    "Empathetic probe question 2",
    "Empathetic probe question 3"
  ],
  "context_indicators": [
    "When to watch for this pattern",
    "How it's typically expressed",
    "What accompanies it"
  ],
  "risk_assessment": {
    "low": "Low risk scenario",
    "medium": "Medium risk scenario",
    "high": "High risk scenario"
  }
}
```

**Example**:
```json
{
  "pattern": "naomba radhi",
  "type": "excessive_apologizing",
  "severity": "medium",
  "cultural_meaning": "I apologize - excessive apologizing may indicate low self-worth, guilt, or fear of conflict. In East African cultures, over-apologizing can signal feeling unworthy of support or fear of burdening others.",
  "interpretation": "The user may have low self-esteem, feel guilty about their feelings, or fear being a burden. This can indicate depression, anxiety, or trauma.",
  "probe_suggestions": [
    "I notice you're apologizing a lot. You don't need to apologize for having feelings - they're valid.",
    "What makes you feel like you need to apologize right now?",
    "You deserve support just like anyone else. What would it feel like to not apologize for needing help?"
  ],
  "context_indicators": [
    "Apologizing multiple times in one conversation",
    "Apologizing for expressing emotions",
    "Apologizing before asking for help"
  ],
  "risk_assessment": {
    "low": "Occasional apologizing, cultural politeness",
    "medium": "Frequent apologizing, low self-worth indicators",
    "high": "Constant apologizing, severe guilt, possible trauma or abuse history"
  }
}
```

### Task 3: Set Up Pinecone (30 minutes) ⚡

**Steps**:

1. **Create Pinecone Account**
   - Go to [https://www.pinecone.io](https://www.pinecone.io)
   - Sign up for free account
   - Verify email

2. **Create Index**
   - Click "Create Index"
   - Name: `cultural-context`
   - Dimensions: `384` (for sentence-transformers/all-MiniLM-L6-v2)
   - Metric: `cosine`
   - Cloud: `AWS`
   - Region: `us-east-1` (or closest to your deployment)
   - Click "Create Index"

3. **Get API Key**
   - Go to "API Keys" in dashboard
   - Copy your API key

4. **Configure Environment**
   - Edit `.env` file or set environment variables:
   ```bash
   PINECONE_API_KEY=your-api-key-here
   PINECONE_INDEX_NAME=cultural-context
   AUTO_INDEX_KB=true
   USE_RAG=true
   ```

5. **Test Configuration**
   ```bash
   # Start the service
   cd apps/backend/services/cultural-context
   python main.py
   
   # In another terminal, test health check
   curl http://localhost:8000/health
   
   # Should see: "vector_db": {"vector_db_type": "pinecone", "connected": true}
   ```

6. **Verify Indexing**
   ```bash
   # Check index stats
   curl http://localhost:8000/health | jq '.vector_db'
   
   # Should show vector_count > 0 after startup
   ```

---

## 📅 Week 1 Plan

### Day 1 (Today): Content Expansion ✅
- ✅ Expand knowledge base (10 new entries)
- ✅ Expand Swahili patterns (10 new patterns)
- ✅ Set up Pinecone

**Deliverables**:
- kb.json with 22+ entries
- swahili_patterns.json with 28+ patterns
- Production vector DB configured

### Day 2: More Content + Testing Setup
**Morning** (2-3 hours):
- Add 8 more KB entries (target: 30 total)
- Add 2 more Swahili patterns (target: 30 total)
- Expand cultural_norms.json

**Afternoon** (2-3 hours):
- Set up integration test framework
- Write first integration test (conversation engine)
- Test vector search performance

**Deliverables**:
- kb.json with 30+ entries
- swahili_patterns.json with 30+ patterns
- First integration test passing

### Day 3: Integration Testing
**Morning** (2-3 hours):
- Write conversation engine integration tests
- Write crisis detection integration tests
- Write RAG service integration tests

**Afternoon** (2-3 hours):
- Write end-to-end user flow tests
- Fix any integration issues discovered
- Verify all tests passing

**Deliverables**:
- Integration test suite complete
- All tests passing
- Integration issues resolved

### Day 4: Performance & Documentation
**Morning** (2-3 hours):
- Performance testing and optimization
- Load testing
- Response time benchmarks

**Afternoon** (2-3 hours):
- Write API documentation with examples
- Write integration guide
- Write troubleshooting guide

**Deliverables**:
- Performance benchmarks met
- Complete API documentation
- Integration guides

### Day 5: Polish & Review
**Morning** (2-3 hours):
- Code review and refactoring
- Security audit
- Final testing

**Afternoon** (2-3 hours):
- Update PROJECT_STATUS.md
- Create deployment checklist
- Prepare for production deployment

**Deliverables**:
- Production-ready service
- Deployment documentation
- Updated project status

---

## 🧪 Testing Commands

### Start Service
```bash
cd apps/backend/services/cultural-context
python main.py
```

### Test Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Get Cultural Context**:
```bash
curl -X GET "http://localhost:8000/context?query=nimechoka&language=sw" \
  -H "Authorization: Bearer test-token"
```

**Cultural Analysis**:
```bash
curl -X POST "http://localhost:8000/cultural-analysis" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am feeling sawa but nimechoka",
    "language": "en",
    "emotion": "sad"
  }'
```

**Bias Check**:
```bash
curl -X POST "http://localhost:8000/bias-check?text=You should just pray more" \
  -H "Authorization: Bearer test-token"
```

**Index Knowledge Base**:
```bash
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
pytest tests/services/cultural-context/ --cov=apps/backend/services/cultural-context --cov-report=html
```

---

## 📊 Progress Tracking

### Daily Checklist

**Day 1** (Today):
- [ ] Add 10 KB entries
- [ ] Add 10 Swahili patterns
- [ ] Set up Pinecone
- [ ] Test vector search
- [ ] Verify auto-indexing

**Day 2**:
- [ ] Add 8 more KB entries (30 total)
- [ ] Add 2 more patterns (30 total)
- [ ] Expand cultural_norms.json
- [ ] Write first integration test
- [ ] Test performance

**Day 3**:
- [ ] Write conversation engine tests
- [ ] Write crisis detection tests
- [ ] Write RAG service tests
- [ ] Write E2E tests
- [ ] Fix integration issues

**Day 4**:
- [ ] Performance testing
- [ ] Load testing
- [ ] Write API documentation
- [ ] Write integration guide
- [ ] Write troubleshooting guide

**Day 5**:
- [ ] Code review
- [ ] Security audit
- [ ] Final testing
- [ ] Update project status
- [ ] Deployment prep

---

## 🎯 Success Metrics

### After Day 1:
- ✅ 22+ KB entries
- ✅ 28+ Swahili patterns
- ✅ Pinecone configured
- ✅ Vector search working

### After Week 1:
- ✅ 30+ KB entries
- ✅ 30+ Swahili patterns
- ✅ Integration tests passing
- ✅ API documentation complete
- ✅ Service at 100% completion

### Performance Targets:
- ✅ <200ms average search response time
- ✅ <500ms average API response time
- ✅ >90% pattern detection accuracy
- ✅ >85% search relevance
- ✅ 95%+ test coverage

---

## 💡 Tips for Success

1. **Use Templates**: Copy existing entries/patterns as templates
2. **Test Incrementally**: Test each new entry/pattern immediately
3. **Focus on Quality**: Better to have 25 great entries than 35 mediocre ones
4. **Document Decisions**: Note why certain patterns are high/medium/low severity
5. **Ask for Help**: Consult cultural experts if unsure about interpretations
6. **Take Breaks**: This is content-heavy work, take breaks to stay fresh

---

## 📚 Resources

### Documentation
- **Implementation Plan**: `CULTURAL_CONTEXT_IMPLEMENTATION_PLAN.md`
- **Quick Wins**: `CULTURAL_CONTEXT_QUICK_WINS.md`
- **Summary**: `CULTURAL_CONTEXT_IMPLEMENTATION_SUMMARY.md`
- **Project Status**: `PROJECT_STATUS.md`

### Code Files
- **Main Service**: `apps/backend/services/cultural-context/main.py`
- **RAG Service**: `apps/backend/services/cultural-context/services/rag_service.py`
- **Deflection Detector**: `apps/backend/services/cultural-context/services/deflection_detector.py`
- **Code Switch Analyzer**: `apps/backend/services/cultural-context/services/code_switch_analyzer.py`

### Data Files
- **Knowledge Base**: `apps/backend/services/cultural-context/data/kb.json`
- **Swahili Patterns**: `apps/backend/services/cultural-context/data/swahili_patterns.json`
- **Cultural Norms**: `apps/backend/services/cultural-context/data/cultural_norms.json`

### Test Files
- **Main Tests**: `tests/services/cultural-context/test_cultural_context.py`
- **RAG Tests**: `tests/services/cultural-context/test_rag_service.py`
- **Deflection Tests**: `tests/services/cultural-context/test_deflection_detector.py`

---

## 🎉 Let's Get Started!

**Your first task**: Open `apps/backend/services/cultural-context/data/kb.json` and add your first new entry about trauma/PTSD in East Africa.

**Remember**: You're building something that will genuinely help people. Every cultural pattern you add, every knowledge base entry you write, makes the system better at understanding and supporting East African communities.

**Good luck!** 🚀

---

**Questions?** Check the documentation files or review existing patterns/entries for examples.

**Stuck?** Look at the 18 existing Swahili patterns and 12 existing KB entries - they're great templates to follow.

**Need inspiration?** Think about common mental health challenges in East African communities and how they're expressed culturally.
