"""
Conversation Simulator for Demo Data Generator

This module generates realistic conversation flows with emotional progression,
cultural context, and English-Swahili code-switching patterns.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..interfaces import ConversationGeneratorInterface
from ..models import (
    ConversationThread, ConversationScenarioType, Message, SpeakerType,
    EmotionResult, EmotionType, CrisisLevel, EmotionalProgression,
    CulturalContext, DemoConfig, GenerationResult
)


class ConversationSimulator(ConversationGeneratorInterface):
    """
    Generates realistic conversation threads with emotional progression
    and cultural context for ResonaAI demo purposes.
    """
    
    def __init__(self):
        self.conversation_templates = self._load_conversation_templates()
        self.swahili_phrases = self._load_swahili_phrases()
        self.emotional_transitions = self._load_emotional_transitions()
        self.crisis_patterns = self._load_crisis_patterns()
    
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate conversations according to configuration"""
        start_time = datetime.now()
        conversations_generated = 0
        errors = []
        warnings = []
        
        try:
            # This would be called by the main orchestrator
            # For now, return a basic result
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            return GenerationResult(
                success=True,
                users_generated=0,  # Not applicable for this generator
                conversations_generated=conversations_generated,
                cultural_scenarios_generated=0,  # Not applicable
                swahili_patterns_generated=0,  # Not applicable
                output_directory=config.output_directory,
                generation_time_seconds=generation_time,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                users_generated=0,
                conversations_generated=conversations_generated,
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=0,
                errors=[str(e)],
                warnings=warnings
            )
    
    def validate_output(self, data) -> bool:
        """Validate generated conversation data"""
        if not isinstance(data, ConversationThread):
            return False
        
        # Check required fields
        if not data.id or not data.user_id or not data.messages:
            return False
        
        # Validate emotional progression
        if not self._validate_emotional_progression(data.emotional_arc):
            return False
        
        # Check message consistency
        for message in data.messages:
            if not message.text or not message.emotion:
                return False
        
        return True
    
    def generate_conversation_thread(self, scenario: ConversationScenarioType, user_id: str) -> ConversationThread:
        """Generate a complete conversation thread for a specific scenario"""
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # Get scenario template
        template = self.conversation_templates.get(scenario, self.conversation_templates[ConversationScenarioType.ACADEMIC_PRESSURE])
        
        # Determine if this should be a crisis conversation
        is_crisis = random.random() < 0.15  # 15% chance for crisis scenarios
        
        if is_crisis:
            template = self._enhance_template_for_crisis(template, scenario)
        
        # Create emotional arc
        emotional_arc = self.create_emotional_arc(
            start_emotion=template["start_emotion"],
            target_emotion=template["target_emotion"],
            steps=template["conversation_length"]
        )
        
        # Adjust crisis level if this is a crisis conversation
        if is_crisis:
            emotional_arc.crisis_level = self._escalate_crisis_level(emotional_arc.crisis_level)
        
        # Generate messages
        messages = self._generate_messages(template, emotional_arc, conversation_id)
        
        # Add crisis escalation patterns if needed
        if is_crisis:
            messages = self._add_crisis_escalation_patterns(messages, scenario)
        
        # Add cultural context to messages
        messages = self._add_cultural_context_to_messages(messages)
        
        conversation = ConversationThread(
            id=conversation_id,
            user_id=user_id,
            scenario=scenario,
            messages=messages,
            emotional_arc=emotional_arc,
            duration_minutes=random.randint(15, 60) if is_crisis else random.randint(10, 45),
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        return self.add_cultural_context(conversation)
    
    def create_emotional_arc(self, start_emotion: str, target_emotion: str, steps: int) -> EmotionalProgression:
        """Create realistic emotional progression between two emotions with validation"""
        # Convert string emotions to EmotionType
        start_emotion_type = EmotionType(start_emotion)
        target_emotion_type = EmotionType(target_emotion)
        
        # Validate input parameters
        if steps < 2:
            steps = 2
        if steps > 20:
            steps = 20
        
        # Generate progression path with validation
        progression = self._generate_emotional_path(start_emotion_type, target_emotion_type, steps)
        
        # Validate the generated progression
        if not self._validate_emotional_progression_realism(progression):
            # Fallback to simple direct progression if validation fails
            progression = self._create_simple_progression(start_emotion_type, target_emotion_type, steps)
        
        # Determine crisis level based on emotions in progression
        crisis_level = self._determine_crisis_level(progression)
        
        return EmotionalProgression(
            start_emotion=start_emotion_type,
            progression=progression,
            end_emotion=target_emotion_type,
            crisis_level=crisis_level
        )
    
    def add_cultural_context(self, conversation: ConversationThread) -> ConversationThread:
        """Add cultural context to conversation"""
        # Add code-switching patterns
        for message in conversation.messages:
            if message.speaker == SpeakerType.USER and random.random() < 0.3:
                message.text = self._add_swahili_code_switching(message.text)
                if message.cultural_context:
                    message.cultural_context.language_switches.append("swahili")
        
        return conversation
    
    def _load_conversation_templates(self) -> Dict[ConversationScenarioType, Dict]:
        """Load conversation templates for different scenarios"""
        return {
            ConversationScenarioType.ACADEMIC_PRESSURE: {
                "start_emotion": "neutral",
                "target_emotion": "sad",
                "conversation_length": 8,
                "user_prompts": [
                    "I'm struggling with my studies lately",
                    "Nimechoka na masomo, sijui nifanye nini",
                    "The pressure is getting too much",
                    "I feel like I'm failing everyone",
                    "Maybe I should just give up"
                ],
                "assistant_responses": [
                    "I understand you're feeling overwhelmed with your studies. Can you tell me more about what's making it difficult?",
                    "Academic pressure can be really challenging. What specific subjects or areas are causing you the most stress?",
                    "It sounds like you're carrying a heavy burden. Have you been able to talk to anyone about how you're feeling?",
                    "Those feelings are valid, but giving up isn't the only option. Let's explore some ways to manage this stress together.",
                    "You mentioned feeling like you're failing everyone. Can you help me understand who you feel you're letting down?"
                ]
            },
            ConversationScenarioType.FAMILY_ISSUES: {
                "start_emotion": "neutral",
                "target_emotion": "angry",
                "conversation_length": 10,
                "user_prompts": [
                    "My family doesn't understand me",
                    "Wazazi wangu hawanielwi",
                    "They expect too much from me",
                    "I can't live up to their expectations",
                    "Sometimes I just want to run away"
                ],
                "assistant_responses": [
                    "Family relationships can be complex. What makes you feel like they don't understand you?",
                    "It sounds like there's a lot of pressure from your family. Can you share what kind of expectations they have?",
                    "Cultural and generational differences can create tension. What specific areas do you clash on?",
                    "Running away might feel like a solution, but let's talk about other ways to address these feelings.",
                    "Have you tried having an open conversation with your family about how their expectations affect you?"
                ]
            },
            ConversationScenarioType.RELATIONSHIP_PROBLEMS: {
                "start_emotion": "sad",
                "target_emotion": "neutral",
                "conversation_length": 6,
                "user_prompts": [
                    "My relationship is falling apart",
                    "Tumeachana na mpenzi wangu",
                    "I don't know how to fix this",
                    "Maybe we're just not meant to be",
                    "I feel so alone now"
                ],
                "assistant_responses": [
                    "Relationship difficulties can be very painful. What's been happening that makes you feel it's falling apart?",
                    "Breakups are never easy. How are you coping with these feelings right now?",
                    "It's natural to feel lost when a relationship ends. What kind of support do you have around you?",
                    "Sometimes relationships end, and that's okay. What matters now is taking care of yourself.",
                    "Loneliness after a breakup is normal. Let's talk about healthy ways to process these emotions."
                ]
            },
            ConversationScenarioType.FINANCIAL_STRESS: {
                "start_emotion": "fear",
                "target_emotion": "neutral",
                "conversation_length": 7,
                "user_prompts": [
                    "I'm worried about money all the time",
                    "Sina pesa ya kutosha",
                    "I don't know how I'll pay for school",
                    "My family is struggling financially",
                    "I feel like such a burden"
                ],
                "assistant_responses": [
                    "Financial stress can be overwhelming. What's your biggest concern about money right now?",
                    "It sounds like you're carrying a lot of worry about finances. Have you been able to explore any options for support?",
                    "Education costs can be daunting. Are there any financial aid resources you've looked into?",
                    "Family financial struggles affect everyone. How is this impacting your daily life and wellbeing?",
                    "You're not a burden. Financial difficulties are challenges that many families face together."
                ]
            }
        }
    
    def _load_swahili_phrases(self) -> Dict[str, str]:
        """Load common Swahili phrases for code-switching"""
        return {
            "I'm tired": "Nimechoka",
            "I don't know": "Sijui",
            "It's difficult": "Ni ngumu",
            "I'm stressed": "Nina stress",
            "My parents": "Wazazi wangu",
            "I can't": "Siwezi",
            "It's okay": "Ni sawa",
            "I'm fine": "Niko sawa",
            "Help me": "Nisaidie",
            "I understand": "Naelewa",
            "Thank you": "Asante",
            "I'm sorry": "Pole",
            "What should I do": "Nifanye nini",
            "I'm worried": "Ninaogopa",
            "It's hard": "Ni ngumu"
        }
    
    def _load_emotional_transitions(self) -> Dict[Tuple[EmotionType, EmotionType], List[EmotionType]]:
        """Load realistic emotional transition paths with intermediate steps"""
        return {
            # Neutral transitions
            (EmotionType.NEUTRAL, EmotionType.SAD): [EmotionType.NEUTRAL, EmotionType.SAD],
            (EmotionType.NEUTRAL, EmotionType.ANGRY): [EmotionType.NEUTRAL, EmotionType.ANGRY],
            (EmotionType.NEUTRAL, EmotionType.FEAR): [EmotionType.NEUTRAL, EmotionType.FEAR],
            (EmotionType.NEUTRAL, EmotionType.HAPPY): [EmotionType.NEUTRAL, EmotionType.HAPPY],
            
            # Sad transitions
            (EmotionType.SAD, EmotionType.NEUTRAL): [EmotionType.SAD, EmotionType.NEUTRAL],
            (EmotionType.SAD, EmotionType.ANGRY): [EmotionType.SAD, EmotionType.ANGRY],
            (EmotionType.SAD, EmotionType.FEAR): [EmotionType.SAD, EmotionType.FEAR],
            (EmotionType.SAD, EmotionType.HAPPY): [EmotionType.SAD, EmotionType.NEUTRAL, EmotionType.HAPPY],
            
            # Angry transitions
            (EmotionType.ANGRY, EmotionType.SAD): [EmotionType.ANGRY, EmotionType.SAD],
            (EmotionType.ANGRY, EmotionType.NEUTRAL): [EmotionType.ANGRY, EmotionType.NEUTRAL],
            (EmotionType.ANGRY, EmotionType.FEAR): [EmotionType.ANGRY, EmotionType.FEAR],
            (EmotionType.ANGRY, EmotionType.HAPPY): [EmotionType.ANGRY, EmotionType.NEUTRAL, EmotionType.HAPPY],
            
            # Fear transitions
            (EmotionType.FEAR, EmotionType.NEUTRAL): [EmotionType.FEAR, EmotionType.NEUTRAL],
            (EmotionType.FEAR, EmotionType.SAD): [EmotionType.FEAR, EmotionType.SAD],
            (EmotionType.FEAR, EmotionType.ANGRY): [EmotionType.FEAR, EmotionType.ANGRY],
            (EmotionType.FEAR, EmotionType.HAPPY): [EmotionType.FEAR, EmotionType.NEUTRAL, EmotionType.HAPPY],
            
            # Happy transitions
            (EmotionType.HAPPY, EmotionType.NEUTRAL): [EmotionType.HAPPY, EmotionType.NEUTRAL],
            (EmotionType.HAPPY, EmotionType.SAD): [EmotionType.HAPPY, EmotionType.NEUTRAL, EmotionType.SAD],
            (EmotionType.HAPPY, EmotionType.SURPRISE): [EmotionType.HAPPY, EmotionType.SURPRISE],
            
            # Surprise transitions
            (EmotionType.SURPRISE, EmotionType.HAPPY): [EmotionType.SURPRISE, EmotionType.HAPPY],
            (EmotionType.SURPRISE, EmotionType.NEUTRAL): [EmotionType.SURPRISE, EmotionType.NEUTRAL],
            (EmotionType.SURPRISE, EmotionType.FEAR): [EmotionType.SURPRISE, EmotionType.FEAR],
            
            # Disgust transitions
            (EmotionType.DISGUST, EmotionType.ANGRY): [EmotionType.DISGUST, EmotionType.ANGRY],
            (EmotionType.DISGUST, EmotionType.NEUTRAL): [EmotionType.DISGUST, EmotionType.NEUTRAL],
        }
    
    def _load_crisis_patterns(self) -> Dict[str, List[str]]:
        """Load crisis escalation patterns with subtle warning signs"""
        return {
            "academic_crisis": [
                "I can't handle the pressure anymore",
                "Maybe I should just drop out",
                "I feel like I'm worthless",
                "Nobody would care if I just disappeared",
                "I don't see the point in trying anymore",
                "Everyone would be better off without me",
                "I'm just a failure at everything",
                "What's the point of living if I can't succeed"
            ],
            "family_crisis": [
                "I hate my family",
                "I want to run away and never come back",
                "They would be better off without me",
                "I feel trapped and hopeless",
                "I don't belong anywhere",
                "I wish I was never born",
                "My family doesn't love me",
                "I'm just a burden to everyone"
            ],
            "relationship_crisis": [
                "I'll never find love again",
                "I'm completely alone in this world",
                "Maybe I'm just meant to be alone",
                "I feel like I'm broken inside",
                "What's the point of trying anymore",
                "Nobody will ever love me",
                "I'm unlovable and worthless",
                "I don't deserve happiness"
            ],
            "financial_crisis": [
                "I can't take this stress anymore",
                "We're going to lose everything",
                "I'm failing my family",
                "I feel so hopeless about the future",
                "Maybe everyone would be better off without me",
                "I can't provide for anyone",
                "I'm a complete failure",
                "There's no way out of this"
            ],
            "subtle_warning_signs": [
                "I've been thinking a lot lately",
                "Sometimes I wonder what the point is",
                "I feel so tired all the time",
                "Nothing seems to matter anymore",
                "I just want the pain to stop",
                "I feel so empty inside",
                "I don't know how much more I can take",
                "I feel like I'm drowning"
            ],
            "safety_responses": [
                "I'm really concerned about what you're sharing. Your life has value and meaning.",
                "It sounds like you're going through an incredibly difficult time. You don't have to face this alone.",
                "I want you to know that there are people who care about you and want to help.",
                "These feelings can be overwhelming, but they can change with proper support.",
                "Have you been able to talk to a counselor or trusted adult about these feelings?",
                "There are crisis resources available 24/7 if you need immediate support.",
                "Your safety is the most important thing right now. Let's talk about getting you help.",
                "You mentioned some very serious thoughts. I want to make sure you're safe."
            ]
        }
    
    def _enhance_template_for_crisis(self, template: Dict, scenario: ConversationScenarioType) -> Dict:
        """Enhance conversation template with crisis elements"""
        enhanced_template = template.copy()
        
        # Get crisis patterns for this scenario
        scenario_key = f"{scenario.value}_crisis"
        crisis_patterns = self.crisis_patterns.get(scenario_key, self.crisis_patterns["subtle_warning_signs"])
        
        # Replace some user prompts with crisis patterns
        enhanced_prompts = template["user_prompts"].copy()
        
        # Start with subtle warning signs
        if len(enhanced_prompts) > 2:
            enhanced_prompts[1] = random.choice(self.crisis_patterns["subtle_warning_signs"])
        
        # Escalate in the middle
        if len(enhanced_prompts) > 4:
            enhanced_prompts[3] = random.choice(crisis_patterns[:4])  # Moderate crisis statements
        
        # Peak crisis near the end
        if len(enhanced_prompts) > 6:
            enhanced_prompts[-2] = random.choice(crisis_patterns[4:])  # Severe crisis statements
        
        enhanced_template["user_prompts"] = enhanced_prompts
        
        # Add safety responses
        enhanced_responses = template["assistant_responses"].copy()
        safety_responses = self.crisis_patterns["safety_responses"]
        
        # Replace later responses with safety-focused ones
        if len(enhanced_responses) > 3:
            enhanced_responses[-2] = random.choice(safety_responses)
            enhanced_responses[-1] = random.choice(safety_responses)
        
        enhanced_template["assistant_responses"] = enhanced_responses
        enhanced_template["target_emotion"] = "fear"  # Crisis conversations often end in fear/concern
        enhanced_template["conversation_length"] = max(template["conversation_length"], 8)  # Longer for crisis
        
        return enhanced_template
    
    def _escalate_crisis_level(self, current_level: CrisisLevel) -> CrisisLevel:
        """Escalate crisis level for crisis conversations"""
        escalation_map = {
            CrisisLevel.NONE: CrisisLevel.MEDIUM,
            CrisisLevel.LOW: CrisisLevel.HIGH,
            CrisisLevel.MEDIUM: CrisisLevel.HIGH,
            CrisisLevel.HIGH: CrisisLevel.CRITICAL,
            CrisisLevel.CRITICAL: CrisisLevel.CRITICAL
        }
        
        return escalation_map.get(current_level, CrisisLevel.HIGH)
    
    def _add_crisis_escalation_patterns(self, messages: List[Message], scenario: ConversationScenarioType) -> List[Message]:
        """Add crisis escalation patterns to messages"""
        # Find user messages and enhance them with crisis indicators
        for i, message in enumerate(messages):
            if message.speaker == SpeakerType.USER:
                # Add crisis-related cultural context
                if message.cultural_context:
                    message.cultural_context.patterns.append("crisis_indicators")
                    message.cultural_context.cultural_significance = "high"
                
                # Increase voice-truth gap for crisis messages (people often hide severity)
                if message.emotion.voice_truth_gap is not None:
                    message.emotion.voice_truth_gap = min(message.emotion.voice_truth_gap * 1.5, 1.0)
                
                # Add crisis-specific Swahili expressions
                if "feel" in message.text.lower() or "tired" in message.text.lower():
                    crisis_swahili = {
                        "I feel hopeless": "Nahisi bila matumaini",
                        "I'm tired": "Nimechoka kabisa",
                        "I can't take it": "Siwezi kuvumilia",
                        "I'm struggling": "Ninapambana sana"
                    }
                    
                    for english, swahili in crisis_swahili.items():
                        if english.lower() in message.text.lower():
                            message.text = message.text.replace(english, swahili)
                            if message.cultural_context:
                                message.cultural_context.language_switches.append("swahili_crisis")
                            break
        
        return messages
    
    def generate_crisis_conversation(self, scenario: ConversationScenarioType, user_id: str) -> ConversationThread:
        """Generate a conversation specifically designed to demonstrate crisis detection"""
        conversation_id = f"crisis_{uuid.uuid4().hex[:8]}"
        
        # Get base template and enhance for crisis
        base_template = self.conversation_templates.get(scenario, self.conversation_templates[ConversationScenarioType.ACADEMIC_PRESSURE])
        crisis_template = self._enhance_template_for_crisis(base_template, scenario)
        
        # Create emotional arc that escalates to crisis
        emotional_arc = EmotionalProgression(
            start_emotion=EmotionType.NEUTRAL,
            progression=[EmotionType.NEUTRAL, EmotionType.SAD, EmotionType.FEAR, EmotionType.SAD, EmotionType.FEAR],
            end_emotion=EmotionType.FEAR,
            crisis_level=CrisisLevel.HIGH
        )
        
        # Generate messages with crisis patterns
        messages = self._generate_messages(crisis_template, emotional_arc, conversation_id)
        messages = self._add_crisis_escalation_patterns(messages, scenario)
        messages = self._add_cultural_context_to_messages(messages)
        
        conversation = ConversationThread(
            id=conversation_id,
            user_id=user_id,
            scenario=scenario,
            messages=messages,
            emotional_arc=emotional_arc,
            duration_minutes=random.randint(20, 60),  # Crisis conversations tend to be longer
            created_at=datetime.now() - timedelta(days=random.randint(0, 7))  # More recent
        )
        
        return self.add_cultural_context(conversation)
    
    def _generate_messages(self, template: Dict, emotional_arc: EmotionalProgression, conversation_id: str) -> List[Message]:
        """Generate messages based on template and emotional arc with appropriate confidence scores"""
        messages = []
        user_prompts = template["user_prompts"]
        assistant_responses = template["assistant_responses"]
        
        for i, emotion in enumerate(emotional_arc.progression):
            # Calculate confidence based on emotion intensity and progression
            confidence = self._calculate_emotion_confidence(emotion, i, len(emotional_arc.progression))
            voice_truth_gap = self._calculate_voice_truth_gap(emotion, emotional_arc.crisis_level)
            
            # User message
            if i < len(user_prompts):
                user_message = Message(
                    id=f"msg_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now() - timedelta(minutes=len(emotional_arc.progression) - i),
                    speaker=SpeakerType.USER,
                    text=user_prompts[i],
                    emotion=EmotionResult(
                        detected=emotion,
                        confidence=confidence,
                        voice_truth_gap=voice_truth_gap
                    ),
                    cultural_context=CulturalContext()
                )
                messages.append(user_message)
            
            # Assistant response
            if i < len(assistant_responses):
                # Assistant emotions are typically more stable and neutral
                assistant_confidence = random.uniform(0.85, 0.95)
                assistant_message = Message(
                    id=f"msg_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.now() - timedelta(minutes=len(emotional_arc.progression) - i - 0.5),
                    speaker=SpeakerType.ASSISTANT,
                    text=assistant_responses[i],
                    emotion=EmotionResult(
                        detected=EmotionType.NEUTRAL,
                        confidence=assistant_confidence
                    )
                )
                messages.append(assistant_message)
        
        return messages
    
    def _calculate_emotion_confidence(self, emotion: EmotionType, position: int, total_steps: int) -> float:
        """Calculate realistic confidence score for emotion detection"""
        base_confidence = {
            EmotionType.NEUTRAL: random.uniform(0.75, 0.90),
            EmotionType.HAPPY: random.uniform(0.80, 0.95),
            EmotionType.SAD: random.uniform(0.70, 0.90),
            EmotionType.ANGRY: random.uniform(0.75, 0.92),
            EmotionType.FEAR: random.uniform(0.65, 0.85),
            EmotionType.SURPRISE: random.uniform(0.60, 0.85),
            EmotionType.DISGUST: random.uniform(0.70, 0.88)
        }
        
        confidence = base_confidence.get(emotion, 0.75)
        
        # Adjust confidence based on position in conversation
        # Early messages might have lower confidence
        if position < total_steps * 0.3:
            confidence *= random.uniform(0.85, 1.0)
        
        # Peak emotional moments have higher confidence
        if total_steps > 4 and position == total_steps // 2:
            confidence *= random.uniform(1.0, 1.1)
        
        return min(confidence, 1.0)
    
    def _calculate_voice_truth_gap(self, emotion: EmotionType, crisis_level: CrisisLevel) -> float:
        """Calculate voice-truth dissonance based on emotion and crisis level"""
        base_gap = {
            EmotionType.NEUTRAL: random.uniform(0.0, 0.15),
            EmotionType.HAPPY: random.uniform(0.0, 0.10),
            EmotionType.SAD: random.uniform(0.10, 0.35),
            EmotionType.ANGRY: random.uniform(0.05, 0.25),
            EmotionType.FEAR: random.uniform(0.15, 0.40),
            EmotionType.SURPRISE: random.uniform(0.0, 0.20),
            EmotionType.DISGUST: random.uniform(0.10, 0.30)
        }
        
        gap = base_gap.get(emotion, 0.15)
        
        # Increase gap for higher crisis levels (people hide emotions more)
        crisis_multiplier = {
            CrisisLevel.NONE: 1.0,
            CrisisLevel.LOW: 1.1,
            CrisisLevel.MEDIUM: 1.3,
            CrisisLevel.HIGH: 1.5,
            CrisisLevel.CRITICAL: 1.8
        }
        
        gap *= crisis_multiplier.get(crisis_level, 1.0)
        
        return min(gap, 1.0)
    
    def _add_cultural_context_to_messages(self, messages: List[Message]) -> List[Message]:
        """Add cultural context to user messages"""
        for message in messages:
            if message.speaker == SpeakerType.USER and message.cultural_context:
                # Add cultural patterns based on message content
                if any(word in message.text.lower() for word in ["family", "parents", "wazazi"]):
                    message.cultural_context.patterns.append("family_dynamics")
                    message.cultural_context.cultural_significance = "high"
                
                if any(word in message.text.lower() for word in ["school", "studies", "masomo"]):
                    message.cultural_context.patterns.append("academic_pressure")
                    message.cultural_context.cultural_significance = "medium"
                
                # Check for deflection patterns
                if any(phrase in message.text.lower() for phrase in ["ni sawa", "it's okay", "i'm fine"]):
                    message.cultural_context.deflection_detected = True
        
        return messages
    
    def _generate_emotional_path(self, start: EmotionType, target: EmotionType, steps: int) -> List[EmotionType]:
        """Generate realistic emotional progression path with intermediate steps"""
        if steps <= 2:
            return [start, target]
        
        # Get predefined path or create one
        path_key = (start, target)
        if path_key in self.emotional_transitions:
            base_path = self.emotional_transitions[path_key].copy()
        else:
            base_path = [start, target]
        
        # If base path is already the right length, return it
        if len(base_path) == steps:
            return base_path
        
        # If we need more steps, interpolate
        if len(base_path) < steps:
            return self._interpolate_emotional_path(base_path, steps)
        
        # If we need fewer steps, compress
        return self._compress_emotional_path(base_path, steps)
    
    def _interpolate_emotional_path(self, base_path: List[EmotionType], target_steps: int) -> List[EmotionType]:
        """Interpolate emotional path to reach target number of steps"""
        if len(base_path) >= target_steps:
            return base_path[:target_steps]
        
        result = [base_path[0]]
        
        # Calculate how many intermediate steps we need
        steps_needed = target_steps - 2  # Subtract start and end
        
        # Define emotional "distances" for realistic transitions
        emotion_groups = {
            'positive': [EmotionType.HAPPY, EmotionType.SURPRISE],
            'neutral': [EmotionType.NEUTRAL],
            'negative': [EmotionType.SAD, EmotionType.ANGRY, EmotionType.FEAR, EmotionType.DISGUST]
        }
        
        current = base_path[0]
        target = base_path[-1]
        
        # Generate intermediate emotions
        for i in range(steps_needed):
            progress = (i + 1) / (steps_needed + 1)
            
            # Choose intermediate emotion based on progress and realism
            if progress < 0.5:
                # Stay closer to start emotion
                intermediate = self._get_nearby_emotion(current)
            else:
                # Move closer to target emotion
                intermediate = self._get_nearby_emotion(target)
            
            # Avoid repeating the same emotion consecutively
            if intermediate != result[-1]:
                result.append(intermediate)
            else:
                # Find alternative emotion
                alternatives = [e for e in EmotionType if e != result[-1]]
                result.append(random.choice(alternatives))
        
        result.append(target)
        return result
    
    def _compress_emotional_path(self, base_path: List[EmotionType], target_steps: int) -> List[EmotionType]:
        """Compress emotional path to target number of steps"""
        if len(base_path) <= target_steps:
            return base_path
        
        # Keep start and end, sample intermediate points
        result = [base_path[0]]
        
        if target_steps > 2:
            # Calculate indices to sample
            step_size = (len(base_path) - 2) / (target_steps - 2)
            for i in range(1, target_steps - 1):
                index = int(1 + (i - 1) * step_size)
                result.append(base_path[min(index, len(base_path) - 2)])
        
        result.append(base_path[-1])
        return result
    
    def _get_nearby_emotion(self, emotion: EmotionType) -> EmotionType:
        """Get an emotion that's realistically close to the given emotion"""
        nearby_emotions = {
            EmotionType.NEUTRAL: [EmotionType.HAPPY, EmotionType.SAD, EmotionType.SURPRISE],
            EmotionType.HAPPY: [EmotionType.NEUTRAL, EmotionType.SURPRISE],
            EmotionType.SAD: [EmotionType.NEUTRAL, EmotionType.ANGRY, EmotionType.FEAR],
            EmotionType.ANGRY: [EmotionType.SAD, EmotionType.DISGUST, EmotionType.NEUTRAL],
            EmotionType.FEAR: [EmotionType.SAD, EmotionType.SURPRISE, EmotionType.NEUTRAL],
            EmotionType.SURPRISE: [EmotionType.HAPPY, EmotionType.FEAR, EmotionType.NEUTRAL],
            EmotionType.DISGUST: [EmotionType.ANGRY, EmotionType.NEUTRAL]
        }
        
        candidates = nearby_emotions.get(emotion, [EmotionType.NEUTRAL])
        return random.choice(candidates)
    
    def _create_simple_progression(self, start: EmotionType, target: EmotionType, steps: int) -> List[EmotionType]:
        """Create a simple emotional progression as fallback"""
        if steps <= 2:
            return [start, target]
        
        result = [start]
        
        # Add neutral as intermediate step if going between different emotions
        if start != target and steps > 2:
            for i in range(steps - 2):
                if i == 0 and start != EmotionType.NEUTRAL:
                    result.append(EmotionType.NEUTRAL)
                else:
                    result.append(start if random.random() < 0.5 else target)
        
        result.append(target)
        return result
    
    def _validate_emotional_progression_realism(self, progression: List[EmotionType]) -> bool:
        """Validate that emotional progression follows realistic patterns"""
        if len(progression) < 2:
            return False
        
        # Check for unrealistic direct transitions
        unrealistic_direct_transitions = [
            (EmotionType.HAPPY, EmotionType.FEAR),
            (EmotionType.HAPPY, EmotionType.DISGUST),
            (EmotionType.SURPRISE, EmotionType.DISGUST),
            (EmotionType.FEAR, EmotionType.HAPPY),
            (EmotionType.DISGUST, EmotionType.HAPPY)
        ]
        
        for i in range(len(progression) - 1):
            current = progression[i]
            next_emotion = progression[i + 1]
            
            # Allow same emotion to continue
            if current == next_emotion:
                continue
            
            # Check for unrealistic transitions
            if (current, next_emotion) in unrealistic_direct_transitions:
                return False
        
        # Check for too many rapid changes
        changes = sum(1 for i in range(len(progression) - 1) 
                     if progression[i] != progression[i + 1])
        
        # More than 70% changes might be unrealistic
        if changes / len(progression) > 0.7:
            return False
        
        return True
    
    def _determine_crisis_level(self, progression: List[EmotionType]) -> CrisisLevel:
        """Determine crisis level based on emotional progression and patterns"""
        # Count negative emotions
        negative_emotions = [EmotionType.SAD, EmotionType.ANGRY, EmotionType.FEAR, EmotionType.DISGUST]
        negative_count = sum(1 for emotion in progression if emotion in negative_emotions)
        
        # Count severe negative emotions (fear is often associated with crisis)
        severe_emotions = [EmotionType.FEAR, EmotionType.DISGUST]
        severe_count = sum(1 for emotion in progression if emotion in severe_emotions)
        
        # Check for emotional instability (rapid changes)
        changes = sum(1 for i in range(len(progression) - 1) 
                     if progression[i] != progression[i + 1])
        instability_ratio = changes / len(progression) if len(progression) > 0 else 0
        
        # Determine crisis level based on multiple factors
        if severe_count >= 2 or (negative_count >= 4 and instability_ratio > 0.6):
            return CrisisLevel.CRITICAL
        elif severe_count >= 1 or (negative_count >= 3 and instability_ratio > 0.4):
            return CrisisLevel.HIGH
        elif negative_count >= 2 or instability_ratio > 0.5:
            return CrisisLevel.MEDIUM
        elif negative_count >= 1:
            return CrisisLevel.LOW
        else:
            return CrisisLevel.NONE
    
    def _add_swahili_code_switching(self, text: str) -> str:
        """Add Swahili code-switching to English text"""
        # Simple replacement of common phrases
        for english, swahili in self.swahili_phrases.items():
            if english.lower() in text.lower():
                # 50% chance to replace with Swahili
                if random.random() < 0.5:
                    text = text.replace(english, swahili)
                    break
        
        return text
    
    def _validate_emotional_progression(self, emotional_arc: EmotionalProgression) -> bool:
        """Validate that emotional progression is realistic"""
        if not emotional_arc.progression:
            return False
        
        # Check that progression starts and ends correctly
        if (emotional_arc.progression[0] != emotional_arc.start_emotion or
            emotional_arc.progression[-1] != emotional_arc.end_emotion):
            return False
        
        # Check for unrealistic jumps (e.g., happy directly to fear)
        unrealistic_transitions = [
            (EmotionType.HAPPY, EmotionType.FEAR),
            (EmotionType.HAPPY, EmotionType.DISGUST),
            (EmotionType.SURPRISE, EmotionType.SAD)
        ]
        
        for i in range(len(emotional_arc.progression) - 1):
            current = emotional_arc.progression[i]
            next_emotion = emotional_arc.progression[i + 1]
            if (current, next_emotion) in unrealistic_transitions:
                return False
        
        return True