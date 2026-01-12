"""
Cultural Knowledge Database for East African Context

This module contains comprehensive cultural knowledge, Swahili patterns,
and cultural scenarios specific to East African communities for the ResonaAI demo system.
"""

from typing import Dict, List, Any
from .models import CrisisLevel


class EastAfricanCulturalKnowledge:
    """
    Comprehensive database of East African cultural knowledge including
    Swahili patterns, cultural scenarios, and appropriate responses.
    """
    
    @staticmethod
    def get_swahili_patterns() -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive Swahili patterns with cultural significance.
        
        Returns patterns commonly used in mental health contexts with
        their meanings, cultural significance, and appropriate responses.
        """
        return {
            # Common expressions of exhaustion and stress
            "nimechoka": {
                "pattern": "nimechoka",
                "meaning": "I'm tired/exhausted",
                "emotional_weight": "medium",
                "cultural_significance": "Often used to express emotional exhaustion, not just physical. Common way to express being overwhelmed.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge the exhaustion and validate the feeling",
                    "Explore what specifically is causing the tiredness",
                    "Offer culturally appropriate coping strategies",
                    "Ask about rest and self-care practices"
                ],
                "context_notes": "Can indicate both physical and emotional exhaustion. Important to explore deeper."
            },
            
            "nimeshindwa": {
                "pattern": "nimeshindwa",
                "meaning": "I'm defeated/I've failed",
                "emotional_weight": "high",
                "cultural_significance": "Strong expression of feeling overwhelmed or defeated. Indicates significant distress.",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate the feeling without minimizing",
                    "Explore what led to feeling defeated",
                    "Help identify small achievable steps",
                    "Discuss resilience and past successes"
                ],
                "context_notes": "Serious expression that warrants careful attention and support."
            },
            
            # Deflection and minimization patterns
            "ni_sawa_tu": {
                "pattern": "ni sawa tu",
                "meaning": "It's just okay/fine",
                "emotional_weight": "low",
                "cultural_significance": "Common deflection phrase to minimize problems. Cultural tendency to not burden others.",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Gently probe deeper with respect",
                    "Acknowledge the cultural tendency to minimize",
                    "Create safe space for honest expression",
                    "Validate that it's okay to share difficulties"
                ],
                "context_notes": "Strong deflection indicator. Often masks deeper issues."
            },
            
            "hakuna_matata": {
                "pattern": "hakuna matata",
                "meaning": "No worries/problems",
                "emotional_weight": "low",
                "cultural_significance": "Popular phrase that can mask serious concerns. May indicate avoidance.",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate the positive outlook",
                    "Gently explore if there are any concerns",
                    "Respect cultural optimism while ensuring safety",
                    "Ask about specific situations that might be challenging"
                ],
                "context_notes": "While positive, can be used to avoid discussing real problems."
            },
            
            "ni_kawaida": {
                "pattern": "ni kawaida",
                "meaning": "It's normal/usual",
                "emotional_weight": "low",
                "cultural_significance": "May minimize serious issues as 'normal'. Can indicate acceptance of problematic situations.",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate that some struggles are common",
                    "Explore what 'normal' means to them",
                    "Gently challenge normalization of distress",
                    "Discuss when 'normal' might need attention"
                ],
                "context_notes": "Important to explore what they consider 'normal' - may mask serious issues."
            },
            
            # Religious and spiritual expressions
            "mungu_atanisaidia": {
                "pattern": "Mungu atanisaidia",
                "meaning": "God will help me",
                "emotional_weight": "high",
                "cultural_significance": "Strong religious faith expression. Indicates reliance on spiritual coping mechanisms.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge and respect their faith",
                    "Explore how faith provides support",
                    "Integrate spiritual coping with practical support",
                    "Ask about their spiritual community"
                ],
                "context_notes": "Respect religious beliefs while ensuring practical support is also available."
            },
            
            "ni_mapenzi_ya_mungu": {
                "pattern": "ni mapenzi ya Mungu",
                "meaning": "It's God's will",
                "emotional_weight": "medium",
                "cultural_significance": "Acceptance of difficult situations through religious framework. May indicate resignation.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Respect the spiritual perspective",
                    "Explore how they understand God's will",
                    "Discuss agency within spiritual beliefs",
                    "Balance acceptance with appropriate action"
                ],
                "context_notes": "Important to balance spiritual acceptance with practical problem-solving."
            },
            
            # Expressions of confusion and helplessness
            "sijui_nifanye_nini": {
                "pattern": "sijui nifanye nini",
                "meaning": "I don't know what to do",
                "emotional_weight": "high",
                "cultural_significance": "Direct expression of helplessness and confusion. Indicates need for guidance.",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Validate the feeling of confusion",
                    "Explore available options together",
                    "Provide structured problem-solving support",
                    "Break down overwhelming situations into manageable parts"
                ],
                "context_notes": "Clear request for help and guidance. Good opportunity for collaborative problem-solving."
            },
            
            "nimechanganyikiwa": {
                "pattern": "nimechanganyikiwa",
                "meaning": "I'm confused/mixed up",
                "emotional_weight": "medium",
                "cultural_significance": "Expression of mental confusion or emotional turmoil.",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Acknowledge the confusion",
                    "Help organize thoughts and feelings",
                    "Explore sources of confusion",
                    "Provide clarity and structure"
                ],
                "context_notes": "Indicates need for help organizing thoughts and emotions."
            },
            
            # Family and social expressions
            "familia_yangu": {
                "pattern": "familia yangu",
                "meaning": "My family",
                "emotional_weight": "medium",
                "cultural_significance": "Family is central to East African identity and decision-making. Often source of both support and pressure.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge the importance of family",
                    "Explore family dynamics and relationships",
                    "Balance individual needs with family expectations",
                    "Discuss healthy family boundaries"
                ],
                "context_notes": "Family context is crucial in East African culture. Explore both positive and challenging aspects."
            },
            
            "wazazi_wangu": {
                "pattern": "wazazi wangu",
                "meaning": "My parents",
                "emotional_weight": "medium",
                "cultural_significance": "Parental authority and expectations are very significant. Often source of pressure and guidance.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Acknowledge parental influence and importance",
                    "Explore parent-child dynamics",
                    "Balance respect for parents with individual autonomy",
                    "Discuss intergenerational differences"
                ],
                "context_notes": "Parental relationships are complex and influential in East African culture."
            },
            
            # Economic and practical concerns
            "sina_pesa": {
                "pattern": "sina pesa",
                "meaning": "I don't have money",
                "emotional_weight": "high",
                "cultural_significance": "Financial stress is common and affects mental health significantly. Often source of shame.",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Acknowledge financial stress without judgment",
                    "Explore practical solutions and resources",
                    "Address mental health impact of financial pressure",
                    "Discuss community and family support systems"
                ],
                "context_notes": "Financial stress significantly impacts mental health. Address both practical and emotional aspects."
            },
            
            "kazi_ni_ngumu": {
                "pattern": "kazi ni ngumu",
                "meaning": "Work is hard/difficult",
                "emotional_weight": "medium",
                "cultural_significance": "Work-related stress is common. May indicate broader life pressures.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Validate work-related stress",
                    "Explore specific work challenges",
                    "Discuss work-life balance",
                    "Address broader life pressures"
                ],
                "context_notes": "Work stress often reflects broader life challenges and pressures."
            },
            
            # Reluctance and shame expressions
            "sitaki_kusema": {
                "pattern": "sitaki kusema",
                "meaning": "I don't want to say",
                "emotional_weight": "medium",
                "cultural_significance": "Indicates reluctance to share, possibly due to shame, cultural taboos, or fear of judgment.",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Respect the boundary and don't pressure",
                    "Create safer space for sharing when ready",
                    "Address potential shame or stigma",
                    "Reassure about confidentiality and non-judgment"
                ],
                "context_notes": "Important to respect boundaries while creating safety for eventual sharing."
            },
            
            "ni_aibu": {
                "pattern": "ni aibu",
                "meaning": "It's shameful/embarrassing",
                "emotional_weight": "high",
                "cultural_significance": "Strong expression of shame. Cultural taboos may be involved.",
                "deflection_indicator": True,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Acknowledge the feeling of shame without judgment",
                    "Explore cultural factors contributing to shame",
                    "Normalize human struggles and imperfections",
                    "Address stigma and cultural taboos sensitively"
                ],
                "context_notes": "Shame is a powerful emotion in East African culture. Handle with great sensitivity."
            },
            
            # Educational and achievement expressions
            "masomo_ni_magumu": {
                "pattern": "masomo ni magumu",
                "meaning": "Studies are difficult",
                "emotional_weight": "medium",
                "cultural_significance": "Academic pressure is significant in East African families. Education seen as path to success.",
                "deflection_indicator": False,
                "crisis_level": "low",
                "appropriate_responses": [
                    "Validate academic challenges",
                    "Explore specific learning difficulties",
                    "Discuss family expectations around education",
                    "Address academic anxiety and pressure"
                ],
                "context_notes": "Academic stress often involves family expectations and economic pressures."
            },
            
            # Health and wellbeing expressions
            "sijisikii_vizuri": {
                "pattern": "sijisikii vizuri",
                "meaning": "I don't feel well",
                "emotional_weight": "medium",
                "cultural_significance": "Can refer to physical or emotional unwellness. Often used for mental health concerns.",
                "deflection_indicator": False,
                "crisis_level": "medium",
                "appropriate_responses": [
                    "Explore both physical and emotional aspects",
                    "Validate the experience of not feeling well",
                    "Discuss the connection between physical and mental health",
                    "Encourage appropriate medical or mental health care"
                ],
                "context_notes": "Important to explore both physical and mental health aspects."
            }
        }
    
    @staticmethod
    def get_cultural_scenarios() -> Dict[str, List[Dict[str, Any]]]:
        """
        Get comprehensive cultural scenarios for East African context.
        
        Returns detailed scenarios covering various cultural conflicts and situations
        commonly encountered in East African communities.
        """
        return {
            "traditional_vs_modern": [
                {
                    "title": "Traditional Healing vs Modern Mental Health Treatment",
                    "description": "A university student experiencing depression faces family pressure to consult traditional healers while wanting to see a counselor. The family believes mental health issues are spiritual problems that require traditional intervention.",
                    "cultural_elements": [
                        "traditional_medicine", "family_expectations", "modern_healthcare", 
                        "cultural_identity", "spiritual_beliefs", "generational_differences"
                    ],
                    "appropriate_responses": [
                        "Respect both traditional and modern approaches",
                        "Explore possibilities for integration",
                        "Address family concerns about modern treatment",
                        "Discuss cultural identity and healing traditions",
                        "Find common ground between approaches"
                    ],
                    "sensitivity_level": "high",
                    "common_phrases": ["dawa za kienyeji", "waganga wa jadi", "mzungu medicine"],
                    "family_dynamics": "Extended family involvement in health decisions",
                    "resolution_strategies": [
                        "Family education about mental health",
                        "Integration of cultural practices with modern treatment",
                        "Gradual introduction of modern concepts"
                    ]
                },
                {
                    "title": "Career Choice vs Family Business Expectations",
                    "description": "A young graduate wants to pursue their passion in arts but faces pressure to join the family business. The family has invested in their education expecting them to contribute to family economic stability.",
                    "cultural_elements": [
                        "family_business", "individual_dreams", "economic_pressure", 
                        "generational_expectations", "family_investment", "cultural_duty"
                    ],
                    "appropriate_responses": [
                        "Explore possibilities for compromise",
                        "Validate both individual dreams and family needs",
                        "Discuss gradual transition strategies",
                        "Address economic realities and family obligations",
                        "Find creative solutions that honor both perspectives"
                    ],
                    "sensitivity_level": "medium",
                    "common_phrases": ["familia kwanza", "umoja ni nguvu", "individual dreams"],
                    "family_dynamics": "Collective decision-making and economic interdependence",
                    "resolution_strategies": [
                        "Phased approach to career transition",
                        "Demonstrating financial viability of chosen path",
                        "Involving respected family members in discussions"
                    ]
                },
                {
                    "title": "Modern Dating vs Traditional Courtship",
                    "description": "Young adults navigating romantic relationships while balancing modern dating practices with traditional courtship expectations from family and community.",
                    "cultural_elements": [
                        "dating_practices", "family_involvement", "cultural_courtship", 
                        "modern_relationships", "community_expectations", "generational_values"
                    ],
                    "appropriate_responses": [
                        "Explore cultural values around relationships",
                        "Discuss communication with family about relationship choices",
                        "Address generational differences in relationship expectations",
                        "Validate both traditional and modern approaches to love"
                    ],
                    "sensitivity_level": "medium",
                    "common_phrases": ["mapenzi ya kisasa", "traditional courtship", "family approval"],
                    "family_dynamics": "Family involvement in relationship decisions",
                    "resolution_strategies": [
                        "Open communication with family about relationship values",
                        "Gradual introduction of partners to family",
                        "Respecting cultural processes while asserting personal choice"
                    ]
                }
            ],
            
            "family_pressure": [
                {
                    "title": "Marriage Pressure and Partner Choice",
                    "description": "A young professional faces intense family pressure to marry someone they don't love, while being in love with someone the family doesn't approve of due to ethnic, religious, or economic differences.",
                    "cultural_elements": [
                        "arranged_marriage", "family_honor", "personal_autonomy", 
                        "cultural_duty", "ethnic_differences", "religious_compatibility"
                    ],
                    "appropriate_responses": [
                        "Validate the emotional conflict and stress",
                        "Explore communication strategies with family",
                        "Discuss cultural negotiation and compromise",
                        "Address the importance of personal happiness in marriage",
                        "Support in finding culturally sensitive solutions"
                    ],
                    "sensitivity_level": "high",
                    "common_phrases": ["ndoa ni harambee", "family choice", "cultural compatibility"],
                    "family_dynamics": "Extended family involvement in marriage decisions",
                    "resolution_strategies": [
                        "Gradual family education about personal choice",
                        "Involving respected community members as mediators",
                        "Demonstrating partner's positive qualities to family"
                    ]
                },
                {
                    "title": "Academic and Career Achievement Pressure",
                    "description": "A student experiencing severe anxiety due to family expectations for academic excellence, professional success, and being the family's hope for economic mobility.",
                    "cultural_elements": [
                        "academic_pressure", "family_pride", "economic_mobility", 
                        "performance_anxiety", "family_investment", "success_expectations"
                    ],
                    "appropriate_responses": [
                        "Address anxiety and stress management",
                        "Explore realistic expectations and goals",
                        "Develop healthy coping strategies for pressure",
                        "Discuss communication with family about stress",
                        "Balance family expectations with personal wellbeing"
                    ],
                    "sensitivity_level": "medium",
                    "common_phrases": ["familia imetegemea", "academic excellence", "family pride"],
                    "family_dynamics": "High investment in children's education and success",
                    "resolution_strategies": [
                        "Setting realistic academic goals",
                        "Family education about mental health and pressure",
                        "Developing stress management techniques"
                    ]
                },
                {
                    "title": "Religious Practice and Personal Beliefs",
                    "description": "Young adult questioning family religious practices while living in a deeply religious household, causing conflict between personal spiritual journey and family expectations.",
                    "cultural_elements": [
                        "religious_expectations", "spiritual_questioning", "family_faith", 
                        "community_belonging", "personal_spirituality", "religious_identity"
                    ],
                    "appropriate_responses": [
                        "Respect both family faith and personal spiritual journey",
                        "Explore meaning-making and spiritual development",
                        "Address community and family belonging concerns",
                        "Support healthy spiritual exploration",
                        "Find ways to maintain family relationships while growing spiritually"
                    ],
                    "sensitivity_level": "high",
                    "common_phrases": ["imani ya familia", "spiritual journey", "religious questioning"],
                    "family_dynamics": "Strong religious identity and community involvement",
                    "resolution_strategies": [
                        "Respectful dialogue about spiritual growth",
                        "Finding common spiritual ground with family",
                        "Gradual communication about personal beliefs"
                    ]
                }
            ],
            
            "gender_expectations": [
                {
                    "title": "Women's Career vs Domestic Role Expectations",
                    "description": "A young woman pursuing career ambitions while facing cultural expectations to prioritize marriage, motherhood, and domestic responsibilities.",
                    "cultural_elements": [
                        "gender_roles", "career_ambitions", "domestic_expectations", 
                        "cultural_change", "women_empowerment", "traditional_roles"
                    ],
                    "appropriate_responses": [
                        "Validate career aspirations and ambitions",
                        "Explore role models and examples of successful women",
                        "Address cultural navigation strategies",
                        "Discuss balancing personal goals with cultural expectations",
                        "Support in challenging limiting gender stereotypes"
                    ],
                    "sensitivity_level": "high",
                    "common_phrases": ["kazi ya kike", "career woman", "family responsibilities"],
                    "family_dynamics": "Traditional gender role expectations from family",
                    "resolution_strategies": [
                        "Demonstrating successful women role models",
                        "Gradual family education about women's capabilities",
                        "Building support networks with like-minded women"
                    ]
                },
                {
                    "title": "Male Emotional Expression and Vulnerability",
                    "description": "A young man struggling to express emotions and seek help due to cultural expectations of male stoicism, strength, and emotional suppression.",
                    "cultural_elements": [
                        "masculine_expectations", "emotional_suppression", "vulnerability", 
                        "cultural_masculinity", "male_strength", "emotional_expression"
                    ],
                    "appropriate_responses": [
                        "Normalize male emotions and vulnerability",
                        "Explore healthy ways to express emotions",
                        "Challenge toxic masculinity concepts",
                        "Discuss strength in emotional awareness",
                        "Support in developing emotional intelligence"
                    ],
                    "sensitivity_level": "medium",
                    "common_phrases": ["mwanaume ni nguvu", "emotional strength", "male vulnerability"],
                    "family_dynamics": "Expectations of male emotional strength and leadership",
                    "resolution_strategies": [
                        "Redefining strength to include emotional awareness",
                        "Finding male role models who express emotions healthily",
                        "Gradual practice of emotional expression in safe spaces"
                    ]
                }
            ],
            
            "religious_conflict": [
                {
                    "title": "Faith Questioning in Religious Community",
                    "description": "An individual questioning religious beliefs while living in a deeply religious family and community, fearing rejection and loss of belonging.",
                    "cultural_elements": [
                        "religious_doubt", "community_belonging", "family_faith", 
                        "personal_spirituality", "religious_identity", "faith_questioning"
                    ],
                    "appropriate_responses": [
                        "Respect the spiritual journey and questioning process",
                        "Explore meaning-making and personal spirituality",
                        "Address community and belonging concerns",
                        "Support healthy spiritual development",
                        "Find ways to maintain relationships while growing spiritually"
                    ],
                    "sensitivity_level": "high",
                    "common_phrases": ["spiritual journey", "faith questioning", "religious community"],
                    "family_dynamics": "Strong religious identity and community involvement",
                    "resolution_strategies": [
                        "Respectful exploration of spiritual questions",
                        "Finding supportive spiritual communities",
                        "Maintaining family relationships while growing spiritually"
                    ]
                }
            ],
            
            "language_identity": [
                {
                    "title": "Code-Switching and Cultural Identity Stress",
                    "description": "A bilingual professional feeling disconnected from cultural identity when required to speak English in professional settings, experiencing stress about losing cultural connection.",
                    "cultural_elements": [
                        "language_identity", "professional_code_switching", "cultural_connection", 
                        "linguistic_pride", "identity_conflict", "cultural_preservation"
                    ],
                    "appropriate_responses": [
                        "Validate linguistic identity and cultural pride",
                        "Explore benefits and challenges of code-switching",
                        "Strengthen cultural connection in personal life",
                        "Discuss ways to honor both languages and cultures",
                        "Address identity integration strategies"
                    ],
                    "sensitivity_level": "medium",
                    "common_phrases": ["lugha ya mama", "professional English", "cultural identity"],
                    "family_dynamics": "Pride in native language and cultural preservation",
                    "resolution_strategies": [
                        "Celebrating multilingual abilities",
                        "Finding ways to incorporate native language in professional settings",
                        "Building cultural pride and identity integration"
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_cultural_responses() -> Dict[str, List[str]]:
        """
        Get appropriate cultural responses for different contexts.
        
        Returns culturally sensitive responses for various situations
        and deflection patterns commonly encountered.
        """
        return {
            "swahili_deflection": [
                "I understand you're using a phrase that might minimize your feelings. In our culture, we sometimes say 'ni sawa tu' even when things aren't okay. Can we explore what's really going on?",
                "That's a common way to express things in Swahili culture, and I respect that. What would it mean to you if we looked a bit deeper at how you're really feeling?",
                "I hear the cultural expression, and I know sometimes we use these phrases to be strong. How are you really feeling underneath?",
                "In our culture, we often say things are 'sawa' even when they're not. It's okay to share what's really happening - this is a safe space."
            ],
            
            "minimization": [
                "It sounds like you might be minimizing your experience, which is very common in our culture. Your feelings are valid and important.",
                "Even if it seems small to you, it's clearly affecting you, and that matters. Let's talk about it.",
                "Sometimes we downplay things that are actually quite significant to us. In our culture, we're taught to be strong, but it's okay to acknowledge when things are difficult.",
                "I notice you're saying it's 'nothing,' but your feelings suggest otherwise. It's okay to give weight to your experiences."
            ],
            
            "comparison_deflection": [
                "While others may face challenges too, your experience matters and deserves attention. We don't need to compare suffering.",
                "Comparing our struggles to others' can sometimes prevent us from addressing our own needs. Your pain is valid regardless of what others are going through.",
                "Your feelings are important regardless of what others are experiencing. Let's focus on what you need right now.",
                "I understand the cultural tendency to think others have it worse, but your struggles deserve care and attention too."
            ],
            
            "religious_spiritual": [
                "I deeply respect your faith and how it provides strength. How can we work together, honoring your spiritual beliefs while also addressing your current struggles?",
                "Your faith is clearly important to you. How do you understand God's role in healing and the help that's available to you?",
                "Many people find great comfort in their faith. Can we explore how your spiritual beliefs and practical support can work together?",
                "I honor your trust in God. Sometimes God works through people and resources to provide help. What might that look like for you?"
            ],
            
            "family_pressure": [
                "Family is so important in our culture, and I can see how much you value their opinions. How can we honor your family while also taking care of your own needs?",
                "I understand the weight of family expectations. It's possible to love and respect your family while also considering what's best for your wellbeing.",
                "Family pressure can be really challenging, especially when we love our families deeply. Let's explore how to navigate this with both respect and self-care.",
                "Your family's opinions matter to you, which shows your good heart. How can we find a way forward that honors both your family and yourself?"
            ],
            
            "shame_stigma": [
                "I can see this feels shameful to you. In our culture, we sometimes feel 'aibu' about things that are actually very human and normal.",
                "There's no shame in struggling or needing help. These are part of the human experience, and you deserve support and understanding.",
                "I understand this feels embarrassing. Many people struggle with similar things, and seeking help shows strength, not weakness.",
                "What you're experiencing doesn't define you or make you less worthy. You deserve compassion, especially from yourself."
            ],
            
            "gender_expectations": [
                "I understand the cultural expectations around [gender roles]. How do you feel about balancing these expectations with your own needs and dreams?",
                "Our culture has certain expectations, and it can be challenging when our personal desires don't align perfectly. Both your cultural identity and personal goals are important.",
                "Gender expectations can create pressure. What would it look like to honor your cultural background while also pursuing what feels right for you?",
                "I see you navigating between cultural expectations and personal aspirations. Both are valid, and we can explore how to honor both."
            ],
            
            "financial_stress": [
                "Financial stress affects so many people, and it can really impact our mental health. There's no shame in struggling financially.",
                "Money worries are very real and can affect every part of our lives. Let's think about both practical steps and ways to manage the emotional impact.",
                "Financial pressure is one of the biggest stressors people face. You're not alone in this, and there may be resources and strategies that can help.",
                "I understand how overwhelming financial stress can be. Let's explore what support might be available and how to cope with this pressure."
            ],
            
            "academic_pressure": [
                "Academic pressure can be intense, especially when family has invested so much in education. How are you managing this stress?",
                "I understand the weight of academic expectations. Education is highly valued in our culture, and that can create a lot of pressure.",
                "It sounds like you're carrying a heavy load with your studies and family expectations. Let's think about ways to manage this pressure while still pursuing your goals.",
                "Academic stress is very real, especially when it feels like the whole family's hopes are riding on your success. How can we support you through this?"
            ],
            
            "neutral": [
                "I'm here to listen and support you. What would be most helpful for you right now?",
                "Can you tell me more about what you're experiencing? I want to understand better.",
                "What's been on your mind lately? I'm here to listen without judgment.",
                "How have you been feeling? Take your time - there's no pressure to share more than you're comfortable with."
            ]
        }
    
    @staticmethod
    def get_deflection_patterns() -> List[Dict[str, Any]]:
        """
        Get patterns that indicate cultural deflection or minimization.
        
        Returns patterns commonly used to deflect or minimize problems
        in East African cultural contexts.
        """
        return [
            {
                "pattern": "I'm fine",
                "confidence": 0.6,
                "cultural_context": "minimization",
                "cultural_notes": "Common across cultures but may mask deeper issues"
            },
            {
                "pattern": "it's nothing",
                "confidence": 0.7,
                "cultural_context": "dismissal",
                "cultural_notes": "Often used to avoid burdening others"
            },
            {
                "pattern": "others have it worse",
                "confidence": 0.8,
                "cultural_context": "comparison_deflection",
                "cultural_notes": "Cultural tendency to minimize own suffering by comparison"
            },
            {
                "pattern": "I can handle it",
                "confidence": 0.6,
                "cultural_context": "self_reliance",
                "cultural_notes": "Cultural value of strength and independence"
            },
            {
                "pattern": "it's just stress",
                "confidence": 0.5,
                "cultural_context": "normalization",
                "cultural_notes": "Normalizing mental health symptoms as 'just stress'"
            },
            {
                "pattern": "ni sawa tu",
                "confidence": 0.8,
                "cultural_context": "swahili_deflection",
                "cultural_notes": "Strong Swahili deflection phrase meaning 'it's just okay'"
            },
            {
                "pattern": "hakuna matata",
                "confidence": 0.7,
                "cultural_context": "swahili_deflection",
                "cultural_notes": "Popular phrase that can mask serious concerns"
            },
            {
                "pattern": "ni kawaida",
                "confidence": 0.7,
                "cultural_context": "swahili_deflection",
                "cultural_notes": "Normalizing problems as 'usual' or 'normal'"
            },
            {
                "pattern": "sitaki kusema",
                "confidence": 0.8,
                "cultural_context": "avoidance",
                "cultural_notes": "Direct avoidance - 'I don't want to say'"
            },
            {
                "pattern": "ni aibu",
                "confidence": 0.9,
                "cultural_context": "shame_deflection",
                "cultural_notes": "Strong shame indicator - 'it's shameful/embarrassing'"
            }
        ]
    
    @staticmethod
    def get_crisis_indicators() -> Dict[str, Dict[str, Any]]:
        """
        Get cultural indicators that may suggest crisis situations.
        
        Returns patterns and phrases that may indicate escalating
        mental health crises in East African cultural contexts.
        """
        return {
            "high_risk_phrases": {
                "nimeshindwa": {
                    "meaning": "I'm defeated/I've failed",
                    "risk_level": "high",
                    "cultural_significance": "Strong expression of hopelessness",
                    "immediate_responses": [
                        "Assess for suicidal ideation",
                        "Explore support systems",
                        "Consider immediate intervention"
                    ]
                },
                "sina_matumaini": {
                    "meaning": "I have no hope",
                    "risk_level": "critical",
                    "cultural_significance": "Direct expression of hopelessness",
                    "immediate_responses": [
                        "Immediate risk assessment",
                        "Crisis intervention protocols",
                        "Emergency support activation"
                    ]
                },
                "nataka_kufa": {
                    "meaning": "I want to die",
                    "risk_level": "critical",
                    "cultural_significance": "Direct suicidal ideation",
                    "immediate_responses": [
                        "Immediate safety assessment",
                        "Crisis intervention",
                        "Emergency services if needed"
                    ]
                }
            },
            
            "escalation_patterns": {
                "increasing_isolation": [
                    "sitaki kuongea na mtu",  # I don't want to talk to anyone
                    "najitenga",  # I'm isolating myself
                    "sina rafiki"  # I have no friends
                ],
                "hopelessness_indicators": [
                    "hakuna mwanga",  # There's no light
                    "maisha ni magumu sana",  # Life is very difficult
                    "sijui kama nitaweza"  # I don't know if I can manage
                ],
                "family_disconnection": [
                    "familia hainifahamu",  # Family doesn't understand me
                    "nimeacha kuongea na wazazi",  # I've stopped talking to parents
                    "nimejitenga na familia"  # I've isolated from family
                ]
            }
        }


class CulturalKnowledgeDatabase:
    """
    Main interface for accessing cultural knowledge database.
    
    Provides structured access to East African cultural knowledge,
    Swahili patterns, and appropriate responses for the demo system.
    """
    
    def __init__(self):
        """Initialize the cultural knowledge database"""
        self.knowledge = EastAfricanCulturalKnowledge()
    
    def get_all_swahili_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all Swahili patterns"""
        return self.knowledge.get_swahili_patterns()
    
    def get_all_cultural_scenarios(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all cultural scenarios"""
        return self.knowledge.get_cultural_scenarios()
    
    def get_all_cultural_responses(self) -> Dict[str, List[str]]:
        """Get all cultural responses"""
        return self.knowledge.get_cultural_responses()
    
    def get_all_deflection_patterns(self) -> List[Dict[str, Any]]:
        """Get all deflection patterns"""
        return self.knowledge.get_deflection_patterns()
    
    def get_crisis_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Get crisis indicators"""
        return self.knowledge.get_crisis_indicators()
    
    def search_patterns_by_meaning(self, search_term: str) -> List[Dict[str, Any]]:
        """Search Swahili patterns by meaning"""
        patterns = self.get_all_swahili_patterns()
        results = []
        
        search_lower = search_term.lower()
        for pattern_id, pattern_data in patterns.items():
            if (search_lower in pattern_data["meaning"].lower() or 
                search_lower in pattern_data["cultural_significance"].lower()):
                result = pattern_data.copy()
                result["id"] = pattern_id
                results.append(result)
        
        return results
    
    def get_scenarios_by_type(self, scenario_type: str) -> List[Dict[str, Any]]:
        """Get scenarios by type"""
        scenarios = self.get_all_cultural_scenarios()
        return scenarios.get(scenario_type, [])
    
    def get_responses_for_context(self, context: str) -> List[str]:
        """Get appropriate responses for cultural context"""
        responses = self.get_all_cultural_responses()
        return responses.get(context, responses.get("neutral", []))