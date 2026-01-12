"""
Cultural Context Analyzer

Analyzes cultural communication patterns including language preferences,
deflection phrases, stoicism, and code-switching patterns.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CulturalContext:
    """Cultural communication patterns"""
    primary_language: str  # 'swahili', 'english', 'mixed'
    code_switching_detected: bool
    code_switching_pattern: Optional[str]  # When/why they switch

    deflection_phrases_used: List[str]  # Cultural deflections detected
    deflection_frequency: float  # How often they deflect

    stoicism_level: str  # 'low', 'medium', 'high'
    stoicism_markers: List[str]

    cultural_stressors: List[str]  # Family duty, economic, etc.

    recommended_approach: str  # How to communicate with them

class CulturalContextAnalyzer:
    """
    Analyzes cultural communication patterns
    """

    def __init__(self):
        # Swahili deflection phrases with cultural meanings
        self.swahili_deflections = {
            'nimechoka': {
                'literal': 'I am tired',
                'cultural': 'Emotionally exhausted, possibly giving up',
                'risk_level': 'high'
            },
            'sawa': {
                'literal': 'Okay/fine',
                'cultural': 'Culturally polite deflection, may not be okay',
                'risk_level': 'medium'
            },
            'sijui': {
                'literal': 'I don\'t know',
                'cultural': 'Overwhelmed, confused, or avoiding',
                'risk_level': 'medium'
            },
            'tutaona': {
                'literal': 'We\'ll see',
                'cultural': 'Fatalistic, giving up control, resignation',
                'risk_level': 'medium'
            }
        }

        # Stoicism markers
        self.stoicism_markers = [
            'managing', 'handling it', 'it\'s fine', 'no big deal',
            'just dealing with it', 'pushing through', 'staying strong'
        ]

    async def analyze(
        self,
        sessions: List[Dict],
        user_id: str
    ) -> CulturalContext:
        """
        Analyze cultural communication patterns
        """
        if not sessions:
            return self._default_context()

        # Extract all transcripts
        transcripts = [
            s.get('transcript', '').lower()
            for s in sessions if s.get('transcript') is not None and s.get('transcript') != ''
        ]

        # 1. Detect language preference
        primary_lang = self._detect_language_preference(transcripts)

        # 2. Detect code-switching
        code_switching, pattern = self._detect_code_switching(transcripts)

        # 3. Find deflection phrases
        deflections_used, deflection_freq = self._detect_deflections(transcripts)

        # 4. Assess stoicism level
        stoicism, markers = self._assess_stoicism(transcripts)

        # 5. Identify cultural stressors
        stressors = self._identify_cultural_stressors(transcripts)

        # 6. Recommend communication approach
        approach = self._recommend_approach(
            primary_lang,
            stoicism,
            deflection_freq
        )

        return CulturalContext(
            primary_language=primary_lang,
            code_switching_detected=code_switching,
            code_switching_pattern=pattern,
            deflection_phrases_used=deflections_used,
            deflection_frequency=deflection_freq,
            stoicism_level=stoicism,
            stoicism_markers=markers,
            cultural_stressors=stressors,
            recommended_approach=approach
        )

    def _detect_language_preference(
        self,
        transcripts: List[str]
    ) -> str:
        """Detect preferred language"""
        swahili_count = 0
        english_count = 0
        mixed_count = 0

        swahili_words = [
            'nimechoka', 'sawa', 'sijui', 'tutaona', 'habari',
            'niko', 'safi', 'poa', 'shida', 'vibaya', 'niambie'
        ]

        for transcript in transcripts:
            has_swahili = any(word in transcript for word in swahili_words)
            has_english = any(word in transcript for word in ['i', 'am', 'the', 'is'])

            if has_swahili and has_english:
                mixed_count += 1
            elif has_swahili:
                swahili_count += 1
            elif has_english:
                english_count += 1

        # Determine primary
        if mixed_count > len(transcripts) * 0.3:
            return 'mixed'
        elif swahili_count > english_count:
            return 'swahili'
        else:
            return 'english'

    def _detect_code_switching(
        self,
        transcripts: List[str]
    ) -> tuple[bool, Optional[str]]:
        """Detect if user code-switches and when"""
        # Simplified: Check if mixing languages
        swahili_words = [
            'nimechoka', 'sawa', 'sijui', 'tutaona', 'habari',
            'niko', 'safi', 'poa', 'shida', 'vibaya'
        ]

        mixed_sessions = 0
        for transcript in transcripts:
            has_swahili = any(word in transcript for word in swahili_words)
            has_english = any(word in transcript for word in ['i', 'am', 'the', 'is'])

            if has_swahili and has_english:
                mixed_sessions += 1

        if mixed_sessions > len(transcripts) * 0.3:
            return True, "Frequently mixes English and Swahili"
        return False, None

    def _detect_deflections(
        self,
        transcripts: List[str]
    ) -> tuple[List[str], float]:
        """Detect cultural deflection phrases"""
        deflections_found = []

        for transcript in transcripts:
            for phrase in self.swahili_deflections.keys():
                if phrase in transcript:
                    deflections_found.append(phrase)

        # Calculate frequency
        frequency = len(deflections_found) / len(transcripts) if transcripts else 0.0

        return list(set(deflections_found)), frequency

    def _assess_stoicism(
        self,
        transcripts: List[str]
    ) -> tuple[str, List[str]]:
        """Assess level of stoicism"""
        markers_found = []

        for transcript in transcripts:
            for marker in self.stoicism_markers:
                if marker in transcript:
                    markers_found.append(marker)

        count = len(markers_found)
        total = len(transcripts)

        if total == 0:
            level = 'low'
        elif count / total > 0.5:
            level = 'high'
        elif count / total > 0.2:
            level = 'medium'
        else:
            level = 'low'

        return level, list(set(markers_found))

    def _identify_cultural_stressors(
        self,
        transcripts: List[str]
    ) -> List[str]:
        """Identify cultural-specific stressors"""
        stressors = []

        stressor_keywords = {
            'family_duty': ['family expects', 'family pressure', 'let my family down', 'disappoint family'],
            'economic': ['can\'t afford', 'money problems', 'financial', 'unemployment'],
            'social_stigma': ['what will people think', 'shame', 'embarrassment', 'reputation'],
            'gender_expectations': ['should be strong', 'man enough', 'good wife', 'good mother']
        }

        combined = ' '.join(transcripts)

        for stressor, keywords in stressor_keywords.items():
            if any(kw in combined for kw in keywords):
                stressors.append(stressor)

        return stressors

    def _recommend_approach(
        self,
        language: str,
        stoicism: str,
        deflection_freq: float
    ) -> str:
        """Recommend how to communicate with this user"""
        if stoicism == 'high' and deflection_freq > 0.3:
            return "permission_based"  # Give permission to be vulnerable
        elif language == 'swahili' or language == 'mixed':
            return "culturally_adapted_swahili"
        elif stoicism == 'low':
            return "direct_empathetic"
        else:
            return "balanced"

    def _default_context(self) -> CulturalContext:
        """Default context for new users"""
        return CulturalContext(
            primary_language='english',
            code_switching_detected=False,
            code_switching_pattern=None,
            deflection_phrases_used=[],
            deflection_frequency=0.0,
            stoicism_level='medium',
            stoicism_markers=[],
            cultural_stressors=[],
            recommended_approach='balanced'
        )
