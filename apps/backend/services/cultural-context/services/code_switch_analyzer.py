"""
Code-switching detection analyzer for English ↔ Swahili transitions
Detects language mixing patterns and correlates with emotional intensity
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .embeddings import get_embedding_service


@dataclass
class CodeSwitchSegment:
    """Represents a segment of text with detected language"""
    text: str
    language: str  # 'en', 'sw', 'mixed', 'unknown'
    start_pos: int
    end_pos: int
    confidence: float


@dataclass
class CodeSwitchTransition:
    """Represents a transition between languages"""
    from_language: str
    to_language: str
    position: int
    context: str
    emotional_intensity: Optional[str] = None


class CodeSwitchAnalyzer:
    """
    Analyzer for detecting code-switching between English and Swahili.
    
    Detects:
    - Language transitions
    - Emotional intensity of transitions
    - Patterns in code-switching behavior
    - Cultural significance of switches
    """
    
    def __init__(self):
        """Initialize code-switching analyzer with language patterns"""
        # Purpose: reuse embedding cosine similarity utility for tests/consistency.
        # Inputs: none.
        # Outputs: sets `self.embedding_service` for cosine similarity.
        # Behavior: uses the cultural-context embedding service (OpenAI or local fallback).
        self.embedding_service = get_embedding_service()

        # Common Swahili words and phrases
        self.swahili_patterns = [
            # Greetings and common phrases
            r'\b(sawa|sijambo|hujambo|hamjambo|mambo|vipi|poa|shida)\b',
            r'\b(asante|asante sana|karibu|pole|pole sana)\b',
            r'\b(ndiyo|hapana|hakuna|kuna|kwa|na|ni|ya|wa|za)\b',
            
            # Emotional words
            r'\b(nimechoka|huzuni|wasiwasi|upweke|hofu|furaha|huzuni)\b',
            r'\b(sijui|tutaona|ni hali ya kawaida|hakuna shida)\b',
            
            # Common verbs
            r'\b(nina|una|tuna|wana|ana|mna|sina|huna|hatuna)\b',
            r'\b(nime|ume|tume|wame|ame|mme|sijui|hujui)\b',
            
            # Common nouns
            r'\b(mtu|watu|nyumba|shule|kazi|pesa|chakula|maji)\b',
            
            # Common adjectives
            r'\b(mzuri|mbaya|nzuri|kubwa|ndogo|refu|fupi)\b',
        ]
        
        # Compile regex patterns
        self.swahili_regex = re.compile(
            '|'.join(self.swahili_patterns),
            re.IGNORECASE
        )
        
        # English indicators (common words that are less likely in Swahili)
        self.english_indicators = [
            r'\b(i|am|are|is|was|were|be|been|being)\b',
            r'\b(you|he|she|it|we|they|me|him|her|us|them)\b',
            r'\b(feel|feeling|felt|feelings|emotion|emotions)\b',
            r'\b(sad|happy|angry|tired|excited|worried|anxious|depressed)\b',
            r'\b(okay|fine|good|bad|well|better|worse)\b',
            r'\b(think|thought|know|knew|understand|understood)\b',
            r'\b(help|helped|support|supported|need|needed|want|wanted)\b',
        ]
        
        self.english_regex = re.compile(
            '|'.join(self.english_indicators),
            re.IGNORECASE
        )
        
        # Emotional intensity markers
        self.high_intensity_markers = [
            r'\b(very|really|extremely|so|too|much|a lot)\b',
            r'\b(cannot|can\'t|couldn\'t|won\'t|wouldn\'t)\b',
            r'\b(always|never|nothing|everything|all|none)\b',
        ]
        
        self.high_intensity_regex = re.compile(
            '|'.join(self.high_intensity_markers),
            re.IGNORECASE
        )
    
    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of a text segment.
        
        Args:
            text: Text segment to analyze
            
        Returns:
            'en', 'sw', 'mixed', or 'unknown'
        """
        if not text or not text.strip():
            return 'unknown'
        
        text_lower = text.lower()
        
        # Count matches
        swahili_matches = len(self.swahili_regex.findall(text_lower))
        english_matches = len(self.english_regex.findall(text_lower))
        
        # Calculate confidence
        total_words = len(text.split())
        if total_words == 0:
            return 'unknown'
        
        swahili_ratio = swahili_matches / total_words if total_words > 0 else 0
        english_ratio = english_matches / total_words if total_words > 0 else 0
        
        # Determine language
        if swahili_ratio > 0.3 and english_ratio < 0.2:
            return 'sw'
        elif english_ratio > 0.3 and swahili_ratio < 0.2:
            return 'en'
        elif swahili_ratio > 0.1 and english_ratio > 0.1:
            return 'mixed'
        else:
            return 'unknown'
    
    def segment_text(self, text: str) -> List[CodeSwitchSegment]:
        """
        Segment text into language-specific segments.
        
        Args:
            text: Full text to segment
            
        Returns:
            List of segments with detected languages
        """
        segments = []

        if not text or not str(text).strip():
            return segments
        
        # Split by sentence boundaries and punctuation
        sentence_pattern = r'([.!?;:]\s+|\n+)'
        parts = re.split(sentence_pattern, str(text))
        
        current_pos = 0
        for i in range(0, len(parts), 2):
            if i < len(parts):
                segment_text = parts[i].strip()
                if segment_text:
                    language = self.detect_language(segment_text)
                    confidence = self._calculate_confidence(segment_text, language)
                    
                    segments.append(CodeSwitchSegment(
                        text=segment_text,
                        language=language,
                        start_pos=current_pos,
                        end_pos=current_pos + len(segment_text),
                        confidence=confidence
                    ))
                    
                    current_pos += len(segment_text)
                
                # Add punctuation if present
                if i + 1 < len(parts):
                    current_pos += len(parts[i + 1])
        
        return segments
    
    def detect_transitions(self, text: str) -> List[CodeSwitchTransition]:
        """
        Detect transitions between languages.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected transitions
        """
        if not text or not str(text).strip():
            return []

        segments = self.segment_text(text)
        transitions = []
        
        for i in range(len(segments) - 1):
            current = segments[i]
            next_seg = segments[i + 1]
            
            # Only consider transitions between distinct languages
            if (current.language != next_seg.language and 
                current.language != 'unknown' and 
                next_seg.language != 'unknown' and
                current.language != 'mixed' and
                next_seg.language != 'mixed'):
                
                # Get context around transition
                context_start = max(0, current.start_pos - 20)
                context_end = min(len(text), next_seg.end_pos + 20)
                context = text[context_start:context_end]
                
                # Assess emotional intensity
                emotional_intensity = self._assess_emotional_intensity(context)
                
                transitions.append(CodeSwitchTransition(
                    from_language=current.language,
                    to_language=next_seg.language,
                    position=current.end_pos,
                    context=context,
                    emotional_intensity=emotional_intensity
                ))
        
        return transitions
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Complete code-switching analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        # Purpose: provide a safe analysis even for None/empty inputs.
        # Inputs: `text` may be None/empty/whitespace.
        # Outputs: dict with stable keys.
        # Behavior: returns a "no signal" analysis for empty inputs instead of raising.
        if not text or not str(text).strip():
            return {
                "code_switching_detected": False,
                "primary_language": "unknown",
                "language_distribution": {},
                "segments": [],
                "transitions": [],
                "emotional_intensity": "low",
                "interpretation": "No text provided for code-switching analysis."
            }

        segments = self.segment_text(text)
        transitions = self.detect_transitions(text)
        
        # Count languages
        language_counts = {}
        for seg in segments:
            lang = seg.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Determine primary language
        primary_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else 'unknown'
        
        # Check for code-switching
        code_switching_detected = len(transitions) > 0 or 'mixed' in language_counts
        
        # Assess overall emotional intensity
        overall_intensity = self._assess_emotional_intensity(str(text))
        
        # Get interpretation
        interpretation = self._generate_interpretation(
            code_switching_detected,
            transitions,
            overall_intensity
        )
        
        return {
            "code_switching_detected": code_switching_detected,
            "primary_language": primary_language,
            "language_distribution": language_counts,
            "segments": [
                {
                    "text": seg.text,
                    "language": seg.language,
                    "confidence": seg.confidence
                }
                for seg in segments
            ],
            "transitions": [
                {
                    "from": trans.from_language,
                    "to": trans.to_language,
                    "position": trans.position,
                    "context": trans.context,
                    "emotional_intensity": trans.emotional_intensity
                }
                for trans in transitions
            ],
            "transition_count": len(transitions),
            "emotional_intensity": overall_intensity,
            "interpretation": interpretation
        }
    
    def _calculate_confidence(self, text: str, language: str) -> float:
        """Calculate confidence in language detection"""
        if language == 'unknown':
            return 0.0
        
        text_lower = text.lower()
        
        if language == 'sw':
            matches = len(self.swahili_regex.findall(text_lower))
            total_words = len(text.split())
            return min(1.0, matches / max(1, total_words * 0.5))
        elif language == 'en':
            matches = len(self.english_regex.findall(text_lower))
            total_words = len(text.split())
            return min(1.0, matches / max(1, total_words * 0.5))
        elif language == 'mixed':
            sw_matches = len(self.swahili_regex.findall(text_lower))
            en_matches = len(self.english_regex.findall(text_lower))
            total_words = len(text.split())
            return min(1.0, (sw_matches + en_matches) / max(1, total_words * 0.3))
        
        return 0.5
    
    def _assess_emotional_intensity(self, text: str) -> str:
        """Assess emotional intensity of text"""
        if not text:
            return 'low'
        
        text_lower = text.lower()
        
        # Count intensity markers
        intensity_matches = len(self.high_intensity_regex.findall(text_lower))
        
        # Count emotional words
        emotional_words = [
            'sad', 'happy', 'angry', 'tired', 'worried', 'anxious',
            'depressed', 'excited', 'fear', 'fearful', 'scared',
            'huzuni', 'wasiwasi', 'upweke', 'hofu', 'nimechoka'
        ]
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        
        # Assess intensity
        if intensity_matches >= 3 or emotional_count >= 3:
            return 'high'
        elif intensity_matches >= 1 or emotional_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_interpretation(self, 
                                code_switching_detected: bool,
                                transitions: List[CodeSwitchTransition],
                                intensity: str) -> str:
        """Generate interpretation of code-switching patterns"""
        if not code_switching_detected:
            return "No code-switching detected. User is using a single language consistently."
        
        if len(transitions) == 0:
            return "Mixed language detected within segments. User may be comfortable with both languages."
        
        # Analyze transition patterns
        high_intensity_transitions = [
            t for t in transitions 
            if t.emotional_intensity == 'high'
        ]
        
        if high_intensity_transitions:
            return (
                f"Code-switching detected with {len(high_intensity_transitions)} high-intensity transitions. "
                "The user may be expressing something important that's easier to say in their native language. "
                "Pay close attention to emotional content during language switches."
            )
        
        if intensity == 'high':
            return (
                "Code-switching detected with high emotional intensity. "
                "The user may be using language switches to express difficult emotions. "
                "Consider the cultural significance of switching languages mid-conversation."
            )
        
        return (
            f"Code-switching detected with {len(transitions)} language transitions. "
            "The user is comfortable with both languages. "
            "Consider asking which language they prefer for deeper conversations."
        )


# Global instance
_analyzer: Optional[CodeSwitchAnalyzer] = None


def get_code_switch_analyzer() -> CodeSwitchAnalyzer:
    """Get or create code-switching analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = CodeSwitchAnalyzer()
    return _analyzer

