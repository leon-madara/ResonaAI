"""
User Profile Generator for Demo Data Generator

This module generates diverse user profiles with:
- Demographic diversity (age, gender, location, language, culture)
- Realistic baseline voice and emotional patterns
- Session history with progression over time
- Authentic East African cultural backgrounds
"""

import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..interfaces import UserGeneratorInterface
from ..models import (
    UserProfile, BaselineData, VoicePatterns, EmotionalPatterns,
    SessionHistory, EmotionType, CrisisLevel, DemoConfig, GenerationResult
)


class UserGenerator(UserGeneratorInterface):
    """Generates diverse user profiles for demo purposes"""
    
    def __init__(self, config: Optional[DemoConfig] = None):
        self.config = config or DemoConfig()
        self.random = random.Random(42)  # Deterministic for reproducible demos
        self.generated_profiles: List[UserProfile] = []  # Store generated profiles
        
        # East African demographic data for authentic profiles
        self.kenyan_ethnic_groups = [
            "Kikuyu", "Luhya", "Luo", "Kalenjin", "Kamba", "Kisii", "Meru",
            "Mijikenda", "Turkana", "Maasai", "Somali", "Borana", "Taita"
        ]
        
        self.kenyan_locations = [
            "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika",
            "Malindi", "Kitale", "Garissa", "Kakamega", "Meru", "Nyeri",
            "Machakos", "Kericho", "Embu", "Migori", "Bungoma", "Homa Bay"
        ]
        
        self.tanzanian_ethnic_groups = [
            "Sukuma", "Nyamwezi", "Chagga", "Hehe", "Makonde", "Yao",
            "Gogo", "Ha", "Haya", "Nyakyusa", "Luguru", "Bena", "Shambaa"
        ]
        
        self.tanzanian_locations = [
            "Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya", "Morogoro",
            "Tanga", "Kahama", "Tabora", "Kigoma", "Sumbawanga", "Kasulu",
            "Songea", "Moshi", "Musoma", "Shinyanga", "Iringa", "Singida"
        ]
        
        self.ugandan_ethnic_groups = [
            "Baganda", "Banyankole", "Basoga", "Bakiga", "Iteso", "Langi",
            "Acholi", "Bagisu", "Lugbara", "Bunyoro", "Batoro", "Alur"
        ]
        
        self.ugandan_locations = [
            "Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Bwizibwera",
            "Mbale", "Mukono", "Kasese", "Masaka", "Entebbe", "Njeru",
            "Kitgum", "Mubende", "Hoima", "Soroti", "Kabale", "Arua"
        ]
        
        # Education levels with realistic distributions
        self.education_levels = [
            ("primary", 0.15),
            ("secondary", 0.25),
            ("high_school", 0.30),
            ("university", 0.25),
            ("postgraduate", 0.05)
        ]
        
        # Occupations with realistic distributions for East Africa
        self.occupations = [
            ("student", 0.30),
            ("teacher", 0.08),
            ("farmer", 0.12),
            ("trader", 0.10),
            ("nurse", 0.05),
            ("driver", 0.06),
            ("mechanic", 0.04),
            ("accountant", 0.03),
            ("engineer", 0.03),
            ("doctor", 0.02),
            ("lawyer", 0.02),
            ("artist", 0.03),
            ("chef", 0.03),
            ("security_guard", 0.04),
            ("shop_keeper", 0.05)
        ]
        
        # Age distributions by occupation
        self.age_by_occupation = {
            "student": (16, 25),
            "teacher": (23, 55),
            "farmer": (25, 65),
            "trader": (20, 60),
            "nurse": (22, 50),
            "driver": (25, 55),
            "mechanic": (20, 50),
            "accountant": (24, 50),
            "engineer": (24, 45),
            "doctor": (26, 55),
            "lawyer": (26, 50),
            "artist": (18, 45),
            "chef": (20, 50),
            "security_guard": (22, 55),
            "shop_keeper": (25, 60)
        }
        
        # Gender distributions by occupation (realistic for East Africa)
        self.gender_by_occupation = {
            "student": {"male": 0.52, "female": 0.48},
            "teacher": {"male": 0.45, "female": 0.55},
            "farmer": {"male": 0.60, "female": 0.40},
            "trader": {"male": 0.55, "female": 0.45},
            "nurse": {"male": 0.25, "female": 0.75},
            "driver": {"male": 0.85, "female": 0.15},
            "mechanic": {"male": 0.90, "female": 0.10},
            "accountant": {"male": 0.55, "female": 0.45},
            "engineer": {"male": 0.70, "female": 0.30},
            "doctor": {"male": 0.60, "female": 0.40},
            "lawyer": {"male": 0.65, "female": 0.35},
            "artist": {"male": 0.60, "female": 0.40},
            "chef": {"male": 0.70, "female": 0.30},
            "security_guard": {"male": 0.80, "female": 0.20},
            "shop_keeper": {"male": 0.50, "female": 0.50}
        }
        
        # Common East African names
        self.male_names = [
            "John", "Peter", "David", "James", "Michael", "Joseph", "Daniel",
            "Samuel", "Paul", "Moses", "Emmanuel", "Francis", "George",
            "Charles", "Robert", "William", "Stephen", "Anthony", "Mark",
            "Juma", "Hassan", "Ali", "Omar", "Salim", "Rashid", "Farid"
        ]
        
        self.female_names = [
            "Mary", "Grace", "Faith", "Joyce", "Jane", "Rose", "Catherine",
            "Margaret", "Elizabeth", "Sarah", "Ruth", "Esther", "Rebecca",
            "Susan", "Agnes", "Lucy", "Nancy", "Patricia", "Christine",
            "Fatuma", "Amina", "Zainab", "Halima", "Khadija", "Maryam"
        ]
        
        # Crisis triggers by demographic
        self.crisis_triggers_by_age = {
            (13, 18): ["academic_pressure", "family_expectations", "peer_pressure", "identity_crisis"],
            (19, 25): ["academic_failure", "career_uncertainty", "relationship_issues", "financial_stress"],
            (26, 35): ["work_pressure", "relationship_problems", "financial_burden", "family_responsibilities"],
            (36, 50): ["health_concerns", "family_issues", "career_stagnation", "financial_stress"],
            (51, 100): ["health_problems", "retirement_anxiety", "family_loss", "social_isolation"]
        }
        
        # Coping mechanisms by cultural background
        self.coping_by_culture = {
            "Kikuyu": ["family_support", "prayer", "community_gathering", "traditional_healing"],
            "Luo": ["music", "storytelling", "family_council", "spiritual_guidance"],
            "Luhya": ["community_work", "traditional_dance", "elder_consultation", "group_prayer"],
            "Kalenjin": ["running", "nature_connection", "age_group_support", "traditional_rituals"],
            "Kamba": ["crafts", "music", "family_unity", "ancestral_guidance"],
            "Maasai": ["warrior_traditions", "cattle_care", "community_ceremonies", "elder_wisdom"],
            "Sukuma": ["farming", "traditional_medicine", "community_support", "cultural_festivals"],
            "Chagga": ["coffee_farming", "mountain_hiking", "cooperative_work", "traditional_brewing"],
            "Baganda": ["drumming", "traditional_dance", "clan_meetings", "royal_traditions"]
        }
    
    def generate_user_profile(self, user_id: str) -> UserProfile:
        """Generate a diverse user profile with realistic demographics and patterns"""
        # Use user_id to ensure consistent generation for the same ID
        user_seed = hash(user_id) % 1000000
        user_random = random.Random(user_seed)
        
        # Select country and corresponding demographics
        country = user_random.choice(["Kenya", "Tanzania", "Uganda"])
        
        if country == "Kenya":
            ethnic_groups = self.kenyan_ethnic_groups
            locations = self.kenyan_locations
        elif country == "Tanzania":
            ethnic_groups = self.tanzanian_ethnic_groups
            locations = self.tanzanian_locations
        else:  # Uganda
            ethnic_groups = self.ugandan_ethnic_groups
            locations = self.ugandan_locations
        
        # Select occupation first as it influences other demographics
        occupation = self._weighted_choice(user_random, self.occupations)
        
        # Generate age based on occupation
        age_range = self.age_by_occupation.get(occupation, (18, 65))
        age = user_random.randint(age_range[0], age_range[1])
        
        # Generate gender based on occupation
        gender_dist = self.gender_by_occupation.get(occupation, {"male": 0.5, "female": 0.5})
        gender = "male" if user_random.random() < gender_dist["male"] else "female"
        
        # Select location and cultural background
        location = f"{user_random.choice(locations)}, {country}"
        cultural_background = user_random.choice(ethnic_groups)
        
        # Generate education level (influenced by age and occupation)
        education_level = self._generate_education_level(user_random, age, occupation)
        
        # Generate languages
        primary_language = "Swahili" if country in ["Kenya", "Tanzania"] else "English"
        secondary_language = "English" if primary_language == "Swahili" else "Swahili"
        
        # Generate baseline data
        baseline_data = self._generate_baseline_data(user_random, age, gender, cultural_background)
        
        # Generate session history
        session_history = self._generate_session_history(user_random, user_id, age, cultural_background)
        
        return UserProfile(
            id=user_id,
            age=age,
            gender=gender,
            location=location,
            primary_language=primary_language,
            secondary_language=secondary_language,
            cultural_background=cultural_background,
            education_level=education_level,
            occupation=occupation,
            baseline_data=baseline_data,
            session_history=session_history
        )
    
    def ensure_demographic_diversity(self, profiles: List[UserProfile]) -> bool:
        """Validate demographic diversity in generated profiles"""
        if not profiles:
            return False
        
        total_profiles = len(profiles)
        
        # Very lenient checks - just ensure some basic variety exists
        # Gender: no requirement (platforms can be gender-dominated)
        
        # Age: just ensure we have some age variety (not all same age)
        ages = [p.age for p in profiles]
        if len(set(ages)) < max(2, total_profiles // 3):
            return False
        
        # Cultural: just ensure at least 2 different cultures for 5+ users
        cultural_groups = set(p.cultural_background for p in profiles)
        if total_profiles >= 5 and len(cultural_groups) < 2:
            return False
        
        # Occupation: just ensure at least 2 different occupations for 5+ users
        occupations = set(p.occupation for p in profiles)
        if total_profiles >= 5 and len(occupations) < 2:
            return False
        
        # Location: just ensure at least 2 different locations for 5+ users
        locations = set(p.location for p in profiles)
        if total_profiles >= 5 and len(locations) < 2:
            return False
        
        return True
    
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate user profiles according to configuration"""
        start_time = datetime.now()
        
        try:
            profiles = []
            max_attempts = config.num_users * 3  # Allow multiple attempts for diversity
            attempts = 0
            
            # Generate initial profiles
            for i in range(config.num_users):
                user_id = f"user_{i+1:03d}"
                profile = self.generate_user_profile(user_id)
                profiles.append(profile)
            
            # Ensure diversity by regenerating if needed
            while not self.ensure_demographic_diversity(profiles) and attempts < max_attempts:
                # Regenerate a random profile to improve diversity
                idx = self.random.randint(0, len(profiles) - 1)
                user_id = f"user_{idx+1:03d}_v{attempts+1}"
                profiles[idx] = self.generate_user_profile(user_id)
                attempts += 1
            
            # Store generated profiles
            self.generated_profiles = profiles
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            warnings = []
            if attempts >= max_attempts:
                warnings.append("Maximum attempts reached for demographic diversity")
            
            return GenerationResult(
                success=True,
                users_generated=len(profiles),
                conversations_generated=0,
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=generation_time,
                warnings=warnings
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                users_generated=0,
                conversations_generated=0,
                cultural_scenarios_generated=0,
                swahili_patterns_generated=0,
                output_directory=config.output_directory,
                generation_time_seconds=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)]
            )
    
    def validate_output(self, data: Any) -> bool:
        """Validate generated user profile meets quality standards"""
        if not isinstance(data, UserProfile):
            return False
        
        # Basic validation
        if not (13 <= data.age <= 100):
            return False
        
        if data.gender not in ["male", "female"]:
            return False
        
        if not data.location or not data.cultural_background:
            return False
        
        if not data.primary_language:
            return False
        
        # Validate baseline data
        if not data.baseline_data:
            return False
        
        if data.baseline_data.voice_patterns.average_pitch <= 0:
            return False
        
        if data.baseline_data.voice_patterns.speech_rate <= 0:
            return False
        
        if not data.baseline_data.emotional_patterns.dominant_emotions:
            return False
        
        return True
    
    # Private helper methods
    
    def _weighted_choice(self, user_random: random.Random, choices: List[tuple]) -> str:
        """Make a weighted random choice from list of (item, weight) tuples"""
        total_weight = sum(weight for _, weight in choices)
        r = user_random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for item, weight in choices:
            cumulative_weight += weight
            if r <= cumulative_weight:
                return item
        
        return choices[-1][0]  # Fallback
    
    def _generate_education_level(self, user_random: random.Random, age: int, occupation: str) -> str:
        """Generate education level based on age and occupation"""
        # Adjust education probabilities based on occupation
        education_adjustments = {
            "doctor": {"university": 0.7, "postgraduate": 0.3},
            "lawyer": {"university": 0.6, "postgraduate": 0.4},
            "engineer": {"university": 0.8, "postgraduate": 0.2},
            "teacher": {"university": 0.6, "postgraduate": 0.2, "high_school": 0.2},
            "nurse": {"university": 0.4, "high_school": 0.6},
            "accountant": {"university": 0.7, "high_school": 0.3},
            "student": {"primary": 0.1, "secondary": 0.3, "high_school": 0.4, "university": 0.2},
            "farmer": {"primary": 0.4, "secondary": 0.4, "high_school": 0.2}
        }
        
        if occupation in education_adjustments:
            adjusted_levels = education_adjustments[occupation]
            choices = [(level, weight) for level, weight in adjusted_levels.items()]
            return self._weighted_choice(user_random, choices)
        
        # Default distribution
        return self._weighted_choice(user_random, self.education_levels)
    
    def _generate_baseline_data(self, user_random: random.Random, age: int, gender: str, culture: str) -> BaselineData:
        """Generate baseline voice and emotional patterns"""
        # Generate voice patterns
        voice_patterns = self._generate_voice_patterns(user_random, age, gender)
        
        # Generate emotional patterns
        emotional_patterns = self._generate_emotional_patterns(user_random, age, culture)
        
        return BaselineData(
            voice_patterns=voice_patterns,
            emotional_patterns=emotional_patterns
        )
    
    def _generate_voice_patterns(self, user_random: random.Random, age: int, gender: str) -> VoicePatterns:
        """Generate realistic voice patterns based on demographics"""
        # Base pitch ranges by gender and age
        if gender == "male":
            base_pitch = user_random.uniform(85, 180)
            if age < 18:
                base_pitch += user_random.uniform(20, 40)  # Higher pitch for younger males
        else:  # female
            base_pitch = user_random.uniform(165, 265)
            if age < 18:
                base_pitch += user_random.uniform(10, 30)  # Slightly higher for younger females
        
        # Age adjustments
        if age > 50:
            base_pitch *= user_random.uniform(0.95, 1.05)  # Slight variation with age
        
        # Speech rate (words per minute)
        base_speech_rate = user_random.uniform(140, 180)
        if age < 25:
            base_speech_rate *= user_random.uniform(1.1, 1.3)  # Younger people speak faster
        elif age > 50:
            base_speech_rate *= user_random.uniform(0.8, 0.95)  # Older people speak slower
        
        # Emotional baseline
        emotional_baseline = user_random.choice([
            EmotionType.NEUTRAL, EmotionType.NEUTRAL, EmotionType.NEUTRAL,  # Most common
            EmotionType.HAPPY, EmotionType.SAD
        ])
        
        # Stress indicators
        possible_indicators = [
            "pitch_elevation", "speech_acceleration", "vocal_tension",
            "breathing_changes", "voice_tremor", "articulation_changes",
            "volume_variation", "pace_irregularity"
        ]
        stress_indicators = user_random.sample(possible_indicators, k=user_random.randint(2, 4))
        
        return VoicePatterns(
            average_pitch=base_pitch,
            speech_rate=base_speech_rate,
            emotional_baseline=emotional_baseline,
            stress_indicators=stress_indicators
        )
    
    def _generate_emotional_patterns(self, user_random: random.Random, age: int, culture: str) -> EmotionalPatterns:
        """Generate emotional patterns based on age and culture"""
        # Dominant emotions vary by age
        if age < 25:
            emotion_pool = [EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SURPRISE, EmotionType.FEAR]
        elif age < 50:
            emotion_pool = [EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SAD, EmotionType.ANGRY]
        else:
            emotion_pool = [EmotionType.NEUTRAL, EmotionType.SAD, EmotionType.HAPPY, EmotionType.FEAR]
        
        dominant_emotions = user_random.sample(emotion_pool, k=user_random.randint(2, 3))
        
        # Crisis triggers based on age
        age_triggers = None
        for age_range, triggers in self.crisis_triggers_by_age.items():
            if age_range[0] <= age <= age_range[1]:
                age_triggers = triggers
                break
        
        if age_triggers:
            crisis_triggers = user_random.sample(age_triggers, k=user_random.randint(1, 3))
        else:
            crisis_triggers = ["general_stress", "life_changes"]
        
        # Coping mechanisms based on culture
        cultural_coping = self.coping_by_culture.get(culture, [
            "family_support", "prayer", "community_support", "traditional_healing"
        ])
        
        # Add some universal coping mechanisms
        universal_coping = ["exercise", "music", "nature", "meditation", "journaling"]
        
        # Ensure at least one cultural coping mechanism is included
        num_coping = user_random.randint(3, 6)
        num_cultural = user_random.randint(1, min(2, len(cultural_coping)))  # At least 1 cultural
        num_universal = num_coping - num_cultural
        
        selected_cultural = user_random.sample(cultural_coping, k=num_cultural)
        selected_universal = user_random.sample(universal_coping, k=min(num_universal, len(universal_coping)))
        
        coping_mechanisms = selected_cultural + selected_universal
        
        return EmotionalPatterns(
            dominant_emotions=dominant_emotions,
            crisis_triggers=crisis_triggers,
            coping_mechanisms=list(set(coping_mechanisms))  # Remove duplicates
        )
    
    def _generate_session_history(self, user_random: random.Random, user_id: str, age: int, culture: str) -> List[SessionHistory]:
        """Generate realistic session history with progression over time"""
        # Number of sessions varies by user engagement
        num_sessions = user_random.randint(1, 8)
        
        sessions = []
        base_date = datetime.now() - timedelta(days=user_random.randint(30, 180))
        
        # Track emotional progression over sessions
        current_crisis_level = CrisisLevel.NONE
        emotional_trajectory = self._generate_emotional_trajectory(user_random, num_sessions)
        
        for i in range(num_sessions):
            session_date = base_date + timedelta(days=user_random.randint(3, 21))
            base_date = session_date
            
            # Session duration varies
            duration = user_random.randint(10, 45)
            
            # Emotional state follows trajectory
            emotional_state = emotional_trajectory[i]
            
            # Crisis level progression
            if i > 0 and user_random.random() < 0.2:  # 20% chance of crisis level change
                crisis_levels = list(CrisisLevel)
                current_idx = crisis_levels.index(current_crisis_level)
                # Slight bias toward improvement over time
                if user_random.random() < 0.6 and current_idx > 0:
                    current_crisis_level = crisis_levels[current_idx - 1]
                elif current_idx < len(crisis_levels) - 1:
                    current_crisis_level = crisis_levels[current_idx + 1]
            
            # Topics discussed based on age and culture
            topics = self._generate_session_topics(user_random, age, culture, emotional_state)
            
            # Intervention needed for higher crisis levels
            intervention_needed = current_crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
            
            session = SessionHistory(
                session_id=f"{user_id}_session_{i+1:02d}",
                date=session_date,
                duration_minutes=duration,
                emotional_state=emotional_state,
                topics_discussed=topics,
                crisis_level=current_crisis_level,
                intervention_needed=intervention_needed
            )
            
            sessions.append(session)
        
        return sessions
    
    def _generate_emotional_trajectory(self, user_random: random.Random, num_sessions: int) -> List[EmotionType]:
        """Generate realistic emotional progression over sessions"""
        if num_sessions == 1:
            return [user_random.choice(list(EmotionType))]
        
        # Start with a random emotion
        trajectory = [user_random.choice([EmotionType.NEUTRAL, EmotionType.SAD, EmotionType.FEAR])]
        
        # Generate progression with slight bias toward improvement
        for i in range(1, num_sessions):
            current_emotion = trajectory[-1]
            
            # Possible next emotions based on current
            if current_emotion == EmotionType.SAD:
                next_options = [EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SAD, EmotionType.ANGRY]
                weights = [0.4, 0.3, 0.2, 0.1]
            elif current_emotion == EmotionType.ANGRY:
                next_options = [EmotionType.NEUTRAL, EmotionType.SAD, EmotionType.ANGRY, EmotionType.HAPPY]
                weights = [0.4, 0.3, 0.2, 0.1]
            elif current_emotion == EmotionType.FEAR:
                next_options = [EmotionType.NEUTRAL, EmotionType.SAD, EmotionType.FEAR, EmotionType.HAPPY]
                weights = [0.4, 0.25, 0.25, 0.1]
            elif current_emotion == EmotionType.NEUTRAL:
                next_options = [EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SAD, EmotionType.SURPRISE]
                weights = [0.4, 0.3, 0.2, 0.1]
            else:  # HAPPY, SURPRISE, DISGUST
                next_options = [EmotionType.NEUTRAL, EmotionType.HAPPY, EmotionType.SAD, EmotionType.SURPRISE]
                weights = [0.3, 0.4, 0.2, 0.1]
            
            next_emotion = user_random.choices(next_options, weights=weights)[0]
            trajectory.append(next_emotion)
        
        return trajectory
    
    def _generate_session_topics(self, user_random: random.Random, age: int, culture: str, emotion: EmotionType) -> List[str]:
        """Generate topics discussed in session based on demographics and emotion"""
        # Base topics by age group
        if age < 25:
            base_topics = [
                "academic_pressure", "career_uncertainty", "relationship_issues",
                "family_expectations", "peer_pressure", "identity_exploration"
            ]
        elif age < 50:
            base_topics = [
                "work_stress", "relationship_problems", "financial_concerns",
                "family_responsibilities", "health_concerns", "career_development"
            ]
        else:
            base_topics = [
                "health_issues", "retirement_planning", "family_relationships",
                "social_isolation", "life_reflection", "legacy_concerns"
            ]
        
        # Add emotion-specific topics
        emotion_topics = {
            EmotionType.SAD: ["depression", "loss", "loneliness", "hopelessness"],
            EmotionType.ANGRY: ["frustration", "injustice", "conflict", "betrayal"],
            EmotionType.FEAR: ["anxiety", "uncertainty", "safety_concerns", "phobias"],
            EmotionType.HAPPY: ["achievements", "relationships", "future_plans", "gratitude"],
            EmotionType.SURPRISE: ["unexpected_events", "new_opportunities", "discoveries"],
            EmotionType.DISGUST: ["moral_conflicts", "ethical_dilemmas", "disappointment"],
            EmotionType.NEUTRAL: ["daily_life", "routine_concerns", "general_wellbeing"]
        }
        
        # Add cultural topics
        cultural_topics = [
            "cultural_identity", "traditional_values", "modern_vs_traditional",
            "language_preservation", "community_expectations", "cultural_practices"
        ]
        
        # Combine and select topics
        all_topics = base_topics + emotion_topics.get(emotion, []) + cultural_topics
        num_topics = user_random.randint(2, 5)
        
        return user_random.sample(all_topics, k=min(num_topics, len(all_topics)))