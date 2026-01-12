"""
Cultural Context Generator for Demo Data

This module generates authentic East African cultural scenarios, Swahili patterns,
and cultural deflection detection patterns for the ResonaAI demo system.
"""

import random
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..interfaces import CulturalGeneratorInterface
from ..models import (
    CulturalScenario, CulturalScenarioType, SwahiliPattern, DeflectionResult,
    CrisisLevel, DemoConfig, GenerationResult
)
from ..cultural_knowledge import CulturalKnowledgeDatabase


class CulturalGenerator(CulturalGeneratorInterface):
    """
    Generates culturally-aware scenarios and patterns specific to East African communities.
    
    This generator creates authentic cultural contexts, Swahili language patterns,
    and simulates cultural deflection detection for the ResonaAI platform.
    """
    
    def __init__(self):
        """Initialize the cultural generator with knowledge base"""
        self.knowledge_db = CulturalKnowledgeDatabase()
        self._swahili_knowledge_base = self.knowledge_db.get_all_swahili_patterns()
        self._cultural_scenarios_base = self.knowledge_db.get_all_cultural_scenarios()
        self._deflection_patterns = self.knowledge_db.get_all_deflection_patterns()
        self._cultural_responses = self.knowledge_db.get_all_cultural_responses()
    
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate cultural data according to configuration"""
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            # Generate Swahili patterns
            swahili_patterns = self.generate_swahili_patterns(config.swahili_patterns)
            
            # Generate cultural scenarios
            cultural_scenarios = []
            for scenario_type in CulturalScenarioType:
                scenarios_per_type = config.cultural_scenarios // len(CulturalScenarioType)
                for _ in range(scenarios_per_type):
                    scenario = self.create_cultural_scenario(scenario_type)
                    cultural_scenarios.append(scenario)
            
            # Add remaining scenarios if needed
            remaining = config.cultural_scenarios - len(cultural_scenarios)
            for _ in range(remaining):
                scenario_type = random.choice(list(CulturalScenarioType))
                scenario = self.create_cultural_scenario(scenario_type)
                cultural_scenarios.append(scenario)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return GenerationResult(
                success=True,
                users_generated=0,  # Not applicable for cultural generator
                conversations_generated=0,  # Not applicable
                cultural_scenarios_generated=len(cultural_scenarios),
                swahili_patterns_generated=len(swahili_patterns),
                output_directory=config.output_directory,
                generation_time_seconds=generation_time,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"Cultural generation failed: {str(e)}")
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return GenerationResult(
                success=False,
                users_generated=0,
                conversations_generated=0,
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=generation_time,
                errors=errors,
                warnings=warnings
            )
    
    def validate_output(self, data: Any) -> bool:
        """Validate generated cultural data meets quality standards"""
        if isinstance(data, list):
            # Validate list of cultural items
            for item in data:
                if isinstance(item, SwahiliPattern):
                    if not self._validate_swahili_pattern(item):
                        return False
                elif isinstance(item, CulturalScenario):
                    if not self._validate_cultural_scenario(item):
                        return False
            return True
        elif isinstance(data, SwahiliPattern):
            return self._validate_swahili_pattern(data)
        elif isinstance(data, CulturalScenario):
            return self._validate_cultural_scenario(data)
        elif isinstance(data, DeflectionResult):
            return self._validate_deflection_result(data)
        
        return False
    
    def generate_swahili_patterns(self, count: int) -> List[SwahiliPattern]:
        """Generate Swahili language patterns with cultural significance"""
        patterns = []
        
        # Ensure we have enough base patterns
        base_patterns = list(self._swahili_knowledge_base.keys())
        
        for i in range(count):
            # Select base pattern (cycle through if we need more than available)
            base_key = base_patterns[i % len(base_patterns)]
            base_pattern = self._swahili_knowledge_base[base_key]
            
            # Create variations for additional patterns
            if i >= len(base_patterns):
                base_pattern = self._create_pattern_variation(base_pattern)
            
            pattern = SwahiliPattern(
                id=f"swahili_{uuid.uuid4().hex[:8]}",
                pattern=base_pattern["pattern"],
                language="swahili",
                meaning=base_pattern["meaning"],
                emotional_weight=base_pattern["emotional_weight"],
                cultural_significance=base_pattern["cultural_significance"],
                deflection_indicator=base_pattern["deflection_indicator"],
                crisis_level=CrisisLevel(base_pattern["crisis_level"]),
                appropriate_responses=base_pattern["appropriate_responses"].copy()
            )
            
            patterns.append(pattern)
        
        return patterns
    
    def create_cultural_scenario(self, scenario_type: CulturalScenarioType) -> CulturalScenario:
        """Create cultural scenario based on type"""
        scenario_templates = self._cultural_scenarios_base.get(scenario_type.value, [])
        
        if not scenario_templates:
            # Fallback scenario
            template = {
                "title": f"General {scenario_type.value.replace('_', ' ').title()} Scenario",
                "description": f"A scenario involving {scenario_type.value.replace('_', ' ')} in East African context",
                "cultural_elements": ["family_dynamics", "community_expectations"],
                "appropriate_responses": ["active_listening", "cultural_sensitivity"],
                "sensitivity_level": "medium"
            }
        else:
            template = random.choice(scenario_templates)
        
        return CulturalScenario(
            id=f"cultural_{uuid.uuid4().hex[:8]}",
            scenario_type=scenario_type,
            title=template["title"],
            description=template["description"],
            cultural_elements=template["cultural_elements"].copy(),
            appropriate_responses=template["appropriate_responses"].copy(),
            sensitivity_level=template["sensitivity_level"]
        )
    
    def simulate_deflection_detection(self, conversation: str) -> DeflectionResult:
        """Simulate cultural deflection detection in conversation text"""
        conversation_lower = conversation.lower()
        detected_patterns = []
        confidence = 0.0
        cultural_context = "neutral"
        
        # Check for deflection patterns
        for pattern_info in self._deflection_patterns:
            if pattern_info["pattern"].lower() in conversation_lower:
                detected_patterns.append(pattern_info["pattern"])
                confidence = max(confidence, pattern_info["confidence"])
                cultural_context = pattern_info["cultural_context"]
        
        # Check for Swahili deflection phrases
        for pattern_key, pattern_data in self._swahili_knowledge_base.items():
            if (pattern_data["deflection_indicator"] and 
                pattern_data["pattern"].lower() in conversation_lower):
                detected_patterns.append(pattern_data["pattern"])
                confidence = max(confidence, 0.8)
                cultural_context = "swahili_deflection"
        
        detected = len(detected_patterns) > 0
        
        # Select appropriate response
        suggested_response = self._get_deflection_response(detected_patterns, cultural_context)
        
        return DeflectionResult(
            detected=detected,
            confidence=confidence,
            patterns=detected_patterns,
            cultural_context=cultural_context,
            suggested_response=suggested_response
        )
    
    def _build_swahili_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive Swahili patterns knowledge base"""
        return {
            "nimechoka": {
                "pattern": "nimechoka",
                "meaning": "I'm tired/exhausted",
                "emotional_weight": "medium",
                "cultural_significance": "Often used to express emotional exhaustion, not just physical",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge the exhaustion",
                    "Explore underlying causes",
                    "Offer culturally appropriate coping strategies"
                ]
            },
            "ni_sawa_tu": {
                "pattern": "ni sawa tu",
                "meaning": "It's just okay/fine",
                "emotional_weight": "low",
                "cultural_significance": "Common deflection phrase to minimize problems",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Gently probe deeper",
                    "Acknowledge the cultural tendency to minimize",
                    "Create safe space for honest expression"
                ]
            },
            "hakuna_matata": {
                "pattern": "hakuna matata",
                "meaning": "No worries/problems",
                "emotional_weight": "low",
                "cultural_significance": "Popular phrase that can mask serious concerns",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate the positive outlook",
                    "Gently explore if there are any concerns",
                    "Respect cultural optimism while ensuring safety"
                ]
            },
            "mungu_atanisaidia": {
                "pattern": "Mungu atanisaidia",
                "meaning": "God will help me",
                "emotional_weight": "high",
                "cultural_significance": "Strong religious faith expression, may indicate reliance on spiritual coping",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge and respect faith",
                    "Explore how faith provides support",
                    "Integrate spiritual coping with practical support"
                ]
            },
            "sijui_nifanye_nini": {
                "pattern": "sijui nifanye nini",
                "meaning": "I don't know what to do",
                "emotional_weight": "high",
                "cultural_significance": "Expression of helplessness and confusion",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate the feeling of confusion",
                    "Explore available options together",
                    "Provide structured problem-solving support"
                ]
            },
            "familia_yangu": {
                "pattern": "familia yangu",
                "meaning": "My family",
                "emotional_weight": "medium",
                "cultural_significance": "Family is central to East African identity and decision-making",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge family importance",
                    "Explore family dynamics",
                    "Balance individual needs with family expectations"
                ]
            },
            "sina_pesa": {
                "pattern": "sina pesa",
                "meaning": "I don't have money",
                "emotional_weight": "high",
                "cultural_significance": "Financial stress is common and affects mental health significantly",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Acknowledge financial stress",
                    "Explore practical solutions",
                    "Address mental health impact of financial pressure"
                ]
            },
            "ni_kawaida": {
                "pattern": "ni kawaida",
                "meaning": "It's normal/usual",
                "emotional_weight": "low",
                "cultural_significance": "May minimize serious issues as 'normal'",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate that some struggles are common",
                    "Explore what 'normal' means to them",
                    "Gently challenge normalization of distress"
                ]
            },
            "sitaki_kusema": {
                "pattern": "sitaki kusema",
                "meaning": "I don't want to say",
                "emotional_weight": "medium",
                "cultural_significance": "Indicates reluctance to share, possibly due to shame or cultural taboos",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Respect the boundary",
                    "Create safer space for sharing",
                    "Address potential shame or stigma"
                ]
            },
            "wazazi_wangu": {
                "pattern": "wazazi wangu",
                "meaning": "My parents",
                "emotional_weight": "medium",
                "cultural_significance": "Parental authority and expectations are very significant in East African culture",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge parental influence",
                    "Explore parent-child dynamics",
                    "Balance respect for parents with individual autonomy"
                ]
            }
        }
    
    def _build_cultural_scenarios_base(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build cultural scenarios knowledge base"""
        return {
            "traditional_vs_modern": [
                {
                    "title": "Traditional Healing vs Modern Therapy",
                    "description": "A young person struggles between family expectations to use traditional healing methods and their desire to seek modern mental health treatment",
                    "cultural_elements": ["traditional_medicine", "family_expectations", "modern_healthcare", "cultural_identity"],
                    "appropriate_responses": ["respect_both_approaches", "explore_integration", "address_family_concerns"],
                    "sensitivity_level": "high"
                },
                {
                    "title": "Career Choice vs Family Business",
                    "description": "University graduate torn between pursuing their passion and joining the family business as expected by tradition",
                    "cultural_elements": ["family_business", "individual_dreams", "economic_pressure", "generational_expectations"],
                    "appropriate_responses": ["explore_compromise", "validate_both_perspectives", "discuss_gradual_transition"],
                    "sensitivity_level": "medium"
                }
            ],
            "family_pressure": [
                {
                    "title": "Marriage Expectations",
                    "description": "Young adult facing intense family pressure to marry someone they don't love, causing significant emotional distress",
                    "cultural_elements": ["arranged_marriage", "family_honor", "personal_autonomy", "cultural_duty"],
                    "appropriate_responses": ["validate_feelings", "explore_communication_with_family", "discuss_cultural_negotiation"],
                    "sensitivity_level": "high"
                },
                {
                    "title": "Academic Achievement Pressure",
                    "description": "Student experiencing anxiety due to family expectations for academic excellence and professional success",
                    "cultural_elements": ["academic_pressure", "family_pride", "economic_mobility", "performance_anxiety"],
                    "appropriate_responses": ["address_anxiety", "explore_realistic_expectations", "develop_coping_strategies"],
                    "sensitivity_level": "medium"
                }
            ],
            "gender_expectations": [
                {
                    "title": "Women's Role Expectations",
                    "description": "Young woman struggling with traditional expectations of domesticity while pursuing career ambitions",
                    "cultural_elements": ["gender_roles", "career_ambitions", "domestic_expectations", "cultural_change"],
                    "appropriate_responses": ["validate_aspirations", "explore_role_models", "address_cultural_navigation"],
                    "sensitivity_level": "high"
                },
                {
                    "title": "Male Emotional Expression",
                    "description": "Young man struggling to express emotions due to cultural expectations of male stoicism and strength",
                    "cultural_elements": ["masculine_expectations", "emotional_suppression", "vulnerability", "cultural_masculinity"],
                    "appropriate_responses": ["normalize_male_emotions", "explore_healthy_expression", "challenge_toxic_masculinity"],
                    "sensitivity_level": "medium"
                }
            ],
            "religious_conflict": [
                {
                    "title": "Faith vs Personal Beliefs",
                    "description": "Individual questioning religious beliefs while living in a deeply religious family and community",
                    "cultural_elements": ["religious_doubt", "community_belonging", "family_faith", "personal_spirituality"],
                    "appropriate_responses": ["respect_spiritual_journey", "explore_meaning_making", "address_community_concerns"],
                    "sensitivity_level": "high"
                }
            ],
            "language_identity": [
                {
                    "title": "Language Code-Switching Stress",
                    "description": "Bilingual individual feeling disconnected from cultural identity when speaking English in professional settings",
                    "cultural_elements": ["language_identity", "professional_code_switching", "cultural_connection", "linguistic_pride"],
                    "appropriate_responses": ["validate_linguistic_identity", "explore_code_switching_benefits", "strengthen_cultural_connection"],
                    "sensitivity_level": "medium"
                }
            ]
        }
    
    def _build_deflection_patterns(self) -> List[Dict[str, Any]]:
        """Build deflection detection patterns"""
        return [
            {
                "pattern": "I'm fine",
                "confidence": 0.6,
                "cultural_context": "minimization"
            },
            {
                "pattern": "it's nothing",
                "confidence": 0.7,
                "cultural_context": "dismissal"
            },
            {
                "pattern": "others have it worse",
                "confidence": 0.8,
                "cultural_context": "comparison_deflection"
            },
            {
                "pattern": "I can handle it",
                "confidence": 0.6,
                "cultural_context": "self_reliance"
            },
            {
                "pattern": "it's just stress",
                "confidence": 0.5,
                "cultural_context": "normalization"
            }
        ]
    
    def _build_cultural_responses(self) -> Dict[str, List[str]]:
        """Build appropriate cultural responses"""
        return {
            "swahili_deflection": [
                "I understand you're using a phrase that might minimize your feelings. Can we explore what's really going on?",
                "That's a common way to express things in Swahili culture. What would it mean to you if we looked deeper?",
                "I hear the cultural expression. How are you really feeling underneath?"
            ],
            "minimization": [
                "It sounds like you might be minimizing your experience. Your feelings are valid.",
                "Even if it seems small to you, it's clearly affecting you. Let's talk about it.",
                "Sometimes we downplay things that are actually quite significant to us."
            ],
            "comparison_deflection": [
                "While others may face challenges too, your experience matters and deserves attention.",
                "Comparing our struggles to others' can sometimes prevent us from addressing our own needs.",
                "Your feelings are valid regardless of what others are going through."
            ],
            "neutral": [
                "I'm here to listen and support you.",
                "Can you tell me more about what you're experiencing?",
                "What would be most helpful for you right now?"
            ]
        }
    
    def _create_pattern_variation(self, base_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Create variations of base patterns for additional content"""
        variation = base_pattern.copy()
        
        # Add slight variations to avoid exact duplicates
        if "tu" not in variation["pattern"]:
            variation["pattern"] = variation["pattern"] + " tu"
            variation["meaning"] = variation["meaning"] + " (emphasis)"
        
        return variation
    
    def _validate_swahili_pattern(self, pattern: SwahiliPattern) -> bool:
        """Validate Swahili pattern data quality"""
        if not pattern.pattern or not pattern.meaning:
            return False
        if pattern.confidence and (pattern.confidence < 0 or pattern.confidence > 1):
            return False
        if not pattern.appropriate_responses:
            return False
        return True
    
    def _validate_cultural_scenario(self, scenario: CulturalScenario) -> bool:
        """Validate cultural scenario data quality"""
        if not scenario.title or not scenario.description:
            return False
        if not scenario.cultural_elements or not scenario.appropriate_responses:
            return False
        if scenario.sensitivity_level not in ["low", "medium", "high"]:
            return False
        return True
    
    def _validate_deflection_result(self, result: DeflectionResult) -> bool:
        """Validate deflection result data quality"""
        if result.confidence < 0 or result.confidence > 1:
            return False
        if not result.suggested_response:
            return False
        return True
    
    def _get_deflection_response(self, patterns: List[str], cultural_context: str) -> str:
        """Get appropriate response for detected deflection patterns"""
        responses = self._cultural_responses.get(cultural_context, self._cultural_responses["neutral"])
        return random.choice(responses)