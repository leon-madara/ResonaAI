"""
Cultural Context Service
Main FastAPI application for cultural context
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone
import os
import json
from typing import Any, Dict, List, Optional

from config import settings
from database import get_db
from repositories.cultural_repository import CulturalRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

KB_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "kb.json")
KB_MOUNT_PATH = "/app/data/cultural-knowledge-base/kb.json"
NORMS_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "cultural_norms.json")
NORMS_MOUNT_PATH = "/app/data/cultural-knowledge-base/cultural_norms.json"


def _load_kb() -> Dict[str, Any]:
    """
    Load cultural knowledge base from either mounted volume path or repo fallback.

    Priority:
    1) Docker volume mount: /app/data/cultural-knowledge-base/kb.json
    2) Repo fallback: services/cultural-context/data/kb.json
    """
    path = KB_MOUNT_PATH if os.path.exists(KB_MOUNT_PATH) else KB_DEFAULT_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_cultural_norms() -> Dict[str, Any]:
    """
    Load cultural norms from either mounted volume path or repo fallback.

    Priority:
    1) Docker volume mount: /app/data/cultural-knowledge-base/cultural_norms.json
    2) Repo fallback: services/cultural-context/data/cultural_norms.json
    
    Returns:
        Dictionary containing cultural norms, communication patterns, bias detection rules,
        local resources, and cultural values. Returns empty dict if file not found.
    """
    path = NORMS_MOUNT_PATH if os.path.exists(NORMS_MOUNT_PATH) else NORMS_DEFAULT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Cultural norms file not found at {path}, using empty norms")
        return {}
    except Exception as e:
        logger.warning(f"Failed to load cultural norms: {e}, using empty norms")
        return {}


def _detect_code_switching(text: str) -> Dict[str, Any]:
    """
    Detect code-switching between English and Swahili.
    
    Returns:
        Dictionary with code_switching detected flag and detected languages.
    """
    try:
        from services.code_switch_analyzer import get_code_switch_analyzer
        analyzer = get_code_switch_analyzer()
        result = analyzer.analyze(text)
        # Normalize keys so the rest of the service can rely on a consistent shape.
        # - Some analyzers report `emotional_intensity`; older fallback uses `intensity`.
        if "intensity" not in result:
            result["intensity"] = result.get("emotional_intensity", "low")
        return result
    except Exception as e:
        logger.warning(f"Code-switching analyzer failed, using fallback: {e}")
        # Fallback to simple detection
        text_lower = text.lower()
        swahili_indicators = [
            "sawa", "nimechoka", "sijambo", "huzuni", "wasiwasi", "upweke",
            "asante", "asante sana", "hofu", "pole", "pole sana", "karibu",
            "mambo", "vipi", "poa", "shida", "hakuna", "hapana", "ndiyo"
        ]
        swahili_words_found = [word for word in swahili_indicators if word in text_lower]
        english_indicators = ["i", "am", "feel", "feeling", "sad", "happy", "tired", "okay", "fine"]
        english_words_found = [word for word in english_indicators if word in text_lower]
        code_switching_detected = len(swahili_words_found) > 0 and len(english_words_found) > 0
        return {
            "code_switching_detected": code_switching_detected,
            "swahili_words": swahili_words_found,
            "english_words": english_words_found,
            "intensity": "high" if len(swahili_words_found) > 2 else "medium" if len(swahili_words_found) > 0 else "low"
        }


def _detect_deflection(text: str, language: str) -> Dict[str, Any]:
    """
    Detect deflection patterns, especially Swahili polite deflections.
    
    Returns:
        Dictionary with deflection detected flag and pattern matched.
    """
    try:
        from services.deflection_detector import get_deflection_detector
        detector = get_deflection_detector()
        result = detector.analyze(text, language=language)
        # Normalize keys so downstream code can safely access `patterns`.
        # - Detector implementations vary; some return `deflections` or `matches` instead.
        if "patterns" not in result:
            result["patterns"] = result.get("deflections", result.get("matches", [])) or []
        return result
    except Exception as e:
        logger.warning(f"Deflection detector failed, using fallback: {e}")
        # Fallback to simple detection
        text_lower = text.lower()
        swahili_deflections = {
            "sawa": "Polite deflection - may indicate not ready to discuss",
            "sijambo": "Stoic response - may mask deeper feelings",
            "hakuna shida": "No problem - may minimize concerns",
            "poa": "Cool/fine - casual deflection"
        }
        english_deflections = {
            "i'm fine": "Common deflection",
            "it's okay": "Minimizing response",
            "no problem": "Dismissive response",
            "nothing": "Stoic response"
        }
        deflection_patterns = swahili_deflections if language == "sw" else english_deflections
        deflection_patterns.update(swahili_deflections)
        detected_deflections = []
        for pattern, meaning in deflection_patterns.items():
            if pattern in text_lower:
                detected_deflections.append({
                    "pattern": pattern,
                    "meaning": meaning,
                    "language": "sw" if pattern in swahili_deflections else "en"
                })
        return {
            "deflection_detected": len(detected_deflections) > 0,
            "patterns": detected_deflections
        }


def _retrieve_entries(kb: Dict[str, Any], query: str, language: str, use_rag: bool = True) -> List[Dict[str, Any]]:
    """
    Retrieve entries using RAG (if available) or keyword-based fallback.

    Purpose:
    - Use semantic search via RAG when vector DB is configured.
    - Fallback to keyword-based retrieval when RAG unavailable.
    - Includes code-switching and deflection detection.
    """
    # Try RAG first if available
    if use_rag:
        try:
            from services.rag_service import get_rag_service
            rag_service = get_rag_service()
            
            if rag_service.is_available():
                rag_results = rag_service.search(query, top_k=3, language=language)
                if rag_results:
                    # Convert RAG results to entry format
                    entries = kb.get("entries", []) or []
                    entry_map = {e.get("id"): e for e in entries}
                    
                    retrieved = []
                    for result in rag_results:
                        entry_id = result.get("id")
                        if entry_id in entry_map:
                            entry = entry_map[entry_id].copy()
                            entry["rag_score"] = result.get("score", 0)
                            retrieved.append(entry)
                    
                    if retrieved:
                        logger.info(f"RAG retrieval found {len(retrieved)} entries")
                        return retrieved
        except Exception as e:
            logger.warning(f"RAG retrieval failed, falling back to keyword search: {e}")
    
    # Fallback to keyword-based retrieval
    q = query.lower()
    entries = kb.get("entries", []) or []

    scored: List[Dict[str, Any]] = []
    for e in entries:
        # Match language or allow cross-language matches for code-switching
        entry_language = e.get("language")
        if entry_language and entry_language not in (None, "", language):
            # Still check if it's a Swahili entry when query might have code-switching
            code_switching_info = _detect_code_switching(query)
            if not (code_switching_info["code_switching_detected"] and entry_language == "sw"):
                continue
        
        keywords = [k.lower() for k in (e.get("keywords") or [])]
        score = sum(1 for k in keywords if k in q)
        if score > 0:
            scored.append({"score": score, "entry": e})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return [s["entry"] for s in scored[:3]]


def _get_cache(context_key: str, db: Session) -> Optional[Dict[str, Any]]:
    """Fetch cached context if present and not expired."""
    try:
        cultural_repo = CulturalRepository(db)
        cache_entry = cultural_repo.get_cached_context(context_key)
        if cache_entry:
            return cache_entry.context_data
        return None
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
        return None


def _set_cache(context_key: str, payload: Dict[str, Any], language: str, db: Session) -> None:
    """Upsert cached context payload (best-effort)."""
    try:
        cultural_repo = CulturalRepository(db)
        cultural_repo.cache_context(
            context_key=context_key,
            context_data=payload,
            language=language,
            region="east_africa",
            expires_in_hours=24
        )
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Cultural Context Service...")
    
    # Initialize RAG service and index knowledge base on startup
    if settings.AUTO_INDEX_KB:
        try:
            from services.rag_service import get_rag_service
            
            logger.info("Initializing RAG service...")
            rag_service = get_rag_service()
            
            # Check vector DB connection
            connection_status = rag_service.check_connection()
            logger.info(f"Vector DB connection status: {connection_status}")
            
            # Ensure index exists (for Pinecone)
            if rag_service.vector_db_type == "pinecone":
                logger.info("Ensuring Pinecone index exists...")
                if rag_service.ensure_index_exists():
                    logger.info("Pinecone index ready")
                else:
                    logger.warning("Failed to ensure Pinecone index exists, falling back to in-memory")
            
            # Load and index knowledge base
            try:
                kb = _load_kb()
                kb_entries = kb.get("entries", [])
                
                if kb_entries:
                    logger.info(f"Indexing {len(kb_entries)} knowledge base entries...")
                    indexed_count = rag_service.index_knowledge_base(kb_entries)
                    logger.info(f"Successfully indexed {indexed_count}/{len(kb_entries)} entries")
                    
                    # Log index stats
                    stats = rag_service.get_index_stats()
                    logger.info(f"Vector DB stats: {stats}")
                else:
                    logger.warning("No knowledge base entries found to index")
                    
            except FileNotFoundError:
                logger.warning("Knowledge base file not found, skipping indexing")
            except Exception as e:
                logger.error(f"Failed to load or index knowledge base: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            logger.info("Service will continue with keyword-based search fallback")
    else:
        logger.info("Auto-indexing disabled (AUTO_INDEX_KB=false)")
    
    yield
    
    logger.info("Shutting down Cultural Context Service...")
    
    # Cleanup vector DB connections
    try:
        from services.rag_service import get_rag_service
        rag_service = get_rag_service()
        
        # Close Weaviate connection if exists
        if rag_service.weaviate_client:
            try:
                rag_service.weaviate_client.close()
                logger.info("Closed Weaviate connection")
            except:
                pass
    except:
        pass

app = FastAPI(title="Cultural Context Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        # Simple query to test connection
        cultural_repo = CulturalRepository(db)
        # Just check if we can create a repo (tests connection)
        db_ok = True
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")
    
    # Check vector DB status
    vector_db_status = {"type": "not_initialized", "connected": False}
    try:
        from services.rag_service import get_rag_service
        rag_service = get_rag_service()
        vector_db_status = rag_service.check_connection()
    except Exception as e:
        vector_db_status["error"] = str(e)

    return {
        "status": "healthy", 
        "service": "cultural-context", 
        "db_connected": db_ok,
        "vector_db": vector_db_status
    }

@app.get("/context")
async def get_cultural_context(
    query: str,
    language: str = "en",
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cultural context for a query"""
    q = (query or "").strip()
    if not q:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="query is required")

    context_key = f"{language}:{q.lower()}"
    cached = _get_cache(context_key, db)
    if cached:
        cached["source"] = "db_cache"
        cached["timestamp"] = datetime.now(timezone.utc).isoformat()
        return cached

    kb = _load_kb()
    cultural_norms = _load_cultural_norms()
    
    # Check if RAG should be used (default: True if available)
    use_rag = os.getenv("USE_RAG", "true").lower() == "true"
    retrieved = _retrieve_entries(kb, q, language, use_rag=use_rag)
    
    # Detect code-switching and deflection
    code_switching_info = _detect_code_switching(q)
    deflection_info = _detect_deflection(q, language)

    # Build context lines, enriched with cultural norms if available
    context_lines = []
    
    # Use cultural norms if available, otherwise use default guidance
    if cultural_norms and "cultural_values" in cultural_norms:
        values = cultural_norms["cultural_values"]
        if "privacy_and_family_reputation" in values:
            context_lines.append(
                "Be mindful of East African norms around privacy, respect, and indirect expression of distress. "
                "Family reputation is highly valued, and mental health issues may be hidden to protect it."
            )
        else:
            context_lines.append(
                "Be mindful of East African norms around privacy, respect, and indirect expression of distress."
            )
        
        if "stigma_and_help_seeking_barriers" in values:
            context_lines.append(
                "Avoid stigmatizing language; normalize help-seeking and community support. "
                "Acknowledge the courage it takes to seek help and frame it as strength, not weakness."
            )
        else:
            context_lines.append(
                "Avoid stigmatizing language; normalize help-seeking and community support."
            )
    else:
        # Fallback to default guidance
        context_lines = [
            "Be mindful of East African norms around privacy, respect, and indirect expression of distress.",
            "Avoid stigmatizing language; normalize help-seeking and community support.",
        ]
    
    # Language preference guidance
    if cultural_norms and "communication_patterns" in cultural_norms:
        comm_patterns = cultural_norms["communication_patterns"]
        if "language_preferences" in comm_patterns:
            context_lines.append(
                "If the user prefers Swahili or code-switching, mirror their language style gently. "
                "Code-switching often indicates emotional intensity - pay attention when language changes."
            )
        else:
            context_lines.append(
                "If the user prefers Swahili or code-switching, mirror their language style gently."
            )
    else:
        context_lines.append(
            "If the user prefers Swahili or code-switching, mirror their language style gently."
        )
    
    # Add code-switching context if detected
    if code_switching_info["code_switching_detected"]:
        context_lines.append(
            f"Code-switching detected (intensity: {code_switching_info['intensity']}). "
            "The user may be expressing something important that's easier to say in their native language. "
            "Pay attention to emotional intensity."
        )
    
    # Add deflection context if detected
    if deflection_info["deflection_detected"]:
        deflection_meanings = [p.get("cultural_meaning", p.get("meaning", "")) for p in deflection_info["patterns"]]
        context_lines.append(
            f"Deflection patterns detected: {', '.join(deflection_meanings)}. "
            "The user may not be ready to discuss their feelings directly. Be patient and offer gentle follow-up."
        )

    retrieval_text = "\n\n".join([e.get("content", "") for e in retrieved if e.get("content")]) if retrieved else ""
    full_context = "\n".join(context_lines) + (("\n\n" + retrieval_text) if retrieval_text else "")

    payload = {
        "cultural_context": [{"id": e.get("id"), "content": e.get("content", ""), "keywords": e.get("keywords", [])} for e in retrieved],
        "context": full_context,
        "language": language,
        "query": q,
        "source": "local_kb_retrieval" if retrieved else "mvp_fallback",
        "matches": [{"id": e.get("id"), "keywords": e.get("keywords")} for e in retrieved],
        "deflection_analysis": deflection_info,
        "code_switching_analysis": code_switching_info,
        "code_switching": code_switching_info,
        "deflection": deflection_info,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Add cultural norms metadata if available
    if cultural_norms:
        payload["cultural_norms_loaded"] = True
        payload["cultural_norms_version"] = cultural_norms.get("version", "unknown")
    else:
        payload["cultural_norms_loaded"] = False

    _set_cache(context_key, payload, language, db)
    return payload


@app.post("/bias-check")
async def check_bias(
    text: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Check text for biases and cultural sensitivity"""
    if not text or not text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="text is required")
    
    try:
        from services.bias_detector import get_bias_detector
        detector = get_bias_detector()
        assessment = detector.assess_overall_sensitivity(text)
        return assessment
    except Exception as e:
        logger.error(f"Bias detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias detection failed: {str(e)}"
        )


@app.post("/index-kb")
async def index_knowledge_base_endpoint(
    clear_existing: bool = False,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Manually trigger knowledge base re-indexing.
    
    Args:
        clear_existing: If True, clear existing vectors before re-indexing
        
    Returns:
        Dictionary with indexing results
    """
    try:
        from services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        # Check if vector DB is available
        if rag_service.vector_db_type == "memory":
            logger.warning("Vector DB not configured, using in-memory storage")
        
        # Clear existing vectors if requested
        if clear_existing:
            logger.info("Clearing existing vectors...")
            if rag_service.clear_index():
                logger.info("Successfully cleared existing vectors")
            else:
                logger.warning("Failed to clear existing vectors")
        
        # Ensure index exists (for Pinecone)
        if rag_service.vector_db_type == "pinecone":
            if not rag_service.ensure_index_exists():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to ensure Pinecone index exists"
                )
        
        # Load and index knowledge base
        try:
            kb = _load_kb()
            kb_entries = kb.get("entries", [])
            
            if not kb_entries:
                return {
                    "success": True,
                    "message": "No knowledge base entries found to index",
                    "indexed_count": 0,
                    "total_entries": 0
                }
            
            logger.info(f"Indexing {len(kb_entries)} knowledge base entries...")
            indexed_count = rag_service.index_knowledge_base(kb_entries)
            
            # Get index stats
            stats = rag_service.get_index_stats()
            
            return {
                "success": True,
                "message": f"Successfully indexed {indexed_count}/{len(kb_entries)} entries",
                "indexed_count": indexed_count,
                "total_entries": len(kb_entries),
                "vector_db_type": rag_service.vector_db_type,
                "stats": stats
            }
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base file not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to index knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index knowledge base: {str(e)}"
        )


# Add request models
class CulturalAnalysisRequest(BaseModel):
    text: str
    language: str = "en"
    emotion: Optional[str] = None
    voice_features: Optional[Dict[str, Any]] = None

@app.post("/cultural-analysis")
async def analyze_cultural_patterns(
    request: CulturalAnalysisRequest,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Comprehensive cultural pattern analysis for conversation engine integration.
    
    This endpoint provides deep cultural analysis including:
    - Deflection pattern detection
    - Code-switching analysis  
    - Cultural context retrieval
    - Voice-text contradiction detection
    - Risk assessment with cultural factors
    
    Returns:
        Comprehensive cultural analysis for conversation engine
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="text is required")
    
    try:
        # Get cultural context using existing logic
        context_response = await get_cultural_context(
            query=request.text,
            language=request.language,
            db=db,
            credentials=credentials
        )
        
        # Enhanced analysis with voice features
        analysis = {
            "text": request.text,
            "language": request.language,
            "emotion": request.emotion,
            "cultural_context": context_response,
            "risk_factors": [],
            "conversation_guidance": {},
            "response_adaptations": []
        }
        
        # Analyze deflection patterns with severity assessment
        deflection_info = context_response.get("deflection_analysis", {})
        if deflection_info.get("deflection_detected"):
            patterns = deflection_info.get("patterns", [])
            high_risk_patterns = [p for p in patterns if p.get("severity") == "high"]
            medium_risk_patterns = [p for p in patterns if p.get("severity") == "medium"]
            critical_risk_patterns = [p for p in patterns if p.get("severity") == "critical"]
            
            if critical_risk_patterns:
                analysis["risk_factors"].append({
                    "type": "critical_risk_deflection",
                    "patterns": critical_risk_patterns,
                    "recommendation": "CRISIS INTERVENTION REQUIRED: Suicide ideation or severe hopelessness detected. Assess safety immediately."
                })
            
            if high_risk_patterns:
                analysis["risk_factors"].append({
                    "type": "high_risk_deflection",
                    "patterns": high_risk_patterns,
                    "recommendation": "Gentle probing needed, possible crisis risk"
                })
            
            if medium_risk_patterns:
                analysis["risk_factors"].append({
                    "type": "medium_risk_deflection", 
                    "patterns": medium_risk_patterns,
                    "recommendation": "Supportive exploration recommended"
                })
        
        # Analyze code-switching with emotional correlation
        code_switching_info = context_response.get("code_switching_analysis", {})
        if code_switching_info.get("code_switching_detected"):
            intensity = code_switching_info.get("intensity", "low")
            analysis["conversation_guidance"]["code_switching"] = {
                "detected": True,
                "intensity": intensity,
                "recommendation": f"Code-switching indicates {intensity} emotional intensity. Consider mirroring language preference."
            }
        
        # Voice-text contradiction analysis
        if request.voice_features and request.emotion:
            contradiction_detected = False
            contradiction_details = []
            
            # Check for common contradictions
            if request.emotion in ["sad", "depressed"] and any(word in request.text.lower() for word in ["fine", "okay", "sawa", "poa"]):
                contradiction_detected = True
                contradiction_details.append({
                    "type": "sad_voice_positive_words",
                    "description": "Voice indicates sadness but words suggest being okay",
                    "severity_multiplier": 1.5
                })
            
            if request.emotion in ["anxious", "stressed"] and any(word in request.text.lower() for word in ["normal", "kawaida", "fine"]):
                contradiction_detected = True
                contradiction_details.append({
                    "type": "anxious_voice_normal_words",
                    "description": "Voice indicates anxiety but words suggest normalcy",
                    "severity_multiplier": 1.3
                })
                contradiction_detected = True
                contradiction_details.append({
                    "type": "anxious_voice_normal_words",
                    "description": "Voice indicates anxiety but words suggest normalcy",
                    "severity_multiplier": 1.3
                })
            
            if contradiction_detected:
                analysis["risk_factors"].append({
                    "type": "voice_text_contradiction",
                    "details": contradiction_details,
                    "recommendation": "Voice and words don't match - gentle exploration of true feelings needed"
                })
        
        # Generate conversation guidance
        cultural_norms = _load_cultural_norms()
        
        # Response adaptation suggestions
        if request.language == "sw" or code_switching_info.get("code_switching_detected"):
            analysis["response_adaptations"].append({
                "type": "language_preference",
                "suggestion": "Consider incorporating Swahili phrases or acknowledging code-switching"
            })
        
        if deflection_info.get("deflection_detected"):
            patterns = deflection_info.get("patterns", [])
            for pattern in patterns:
                probe_suggestions = pattern.get("probe_suggestions", [])
                if probe_suggestions:
                    analysis["response_adaptations"].append({
                        "type": "deflection_response",
                        "pattern": pattern.get("pattern"),
                        "suggestions": probe_suggestions[:2]  # Top 2 suggestions
                    })
        
        # Cultural sensitivity guidance
        if cultural_norms:
            values = cultural_norms.get("cultural_values", {})
            if "privacy_and_family_reputation" in values:
                analysis["conversation_guidance"]["privacy"] = {
                    "importance": "high",
                    "recommendation": "Emphasize confidentiality and frame help-seeking as protecting family"
                }
            
            if "spiritual_and_religious_beliefs" in values:
                analysis["conversation_guidance"]["spirituality"] = {
                    "importance": "high", 
                    "recommendation": "Respect spiritual beliefs and integrate them into support"
                }
        
        # Overall risk assessment
        risk_level = "low"
        if any(rf["type"] == "critical_risk_deflection" for rf in analysis["risk_factors"]):
            risk_level = "critical"
        elif any(rf["type"] == "high_risk_deflection" for rf in analysis["risk_factors"]):
            risk_level = "high"
        elif any(rf["type"] in ["medium_risk_deflection", "voice_text_contradiction"] for rf in analysis["risk_factors"]):
            risk_level = "medium"
        
        analysis["overall_risk_level"] = risk_level
        analysis["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cultural analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cultural analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.SERVICE_PORT)

