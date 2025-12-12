"""
GPT-4 Service for generating therapeutic responses
"""

import logging
from typing import Dict, Optional, List
import asyncio
try:
    import openai
except ImportError:
    # Fallback for older openai versions
    openai = None

logger = logging.getLogger(__name__)


class GPTService:
    """Service for interacting with OpenAI GPT-4"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", max_tokens: int = 500, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # OpenAI library may not be installed in some environments.
        if api_key and openai is not None and hasattr(openai, "api_key"):
            openai.api_key = api_key
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        emotion_context: Optional[Dict] = None,
        dissonance_context: Optional[Dict] = None,
        cultural_context: Optional[Dict] = None
    ) -> str:
        """
        Generate empathetic response using GPT-4
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
            emotion_context: Current emotion detection
            dissonance_context: Dissonance analysis results
            cultural_context: Cultural context information
        
        Returns:
            Generated response text
        """
        if not self.api_key or openai is None:
            logger.warning("OpenAI API key not configured, returning default response")
            return self._default_response(user_message, emotion_context)
        
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(emotion_context, dissonance_context, cultural_context)
            
            # Build messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            if hasattr(openai, 'ChatCompletion'):
                # OpenAI v0.x
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content.strip()
            elif hasattr(openai, 'OpenAI'):
                # OpenAI v1.x
                def _call():
                    client = openai.OpenAI(api_key=self.api_key)
                    return client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )

                response = await asyncio.to_thread(_call)
                return response.choices[0].message.content.strip()
            else:
                raise Exception("OpenAI library not properly configured")
            
        except Exception as e:
            logger.error(f"Error generating GPT response: {e}")
            return self._default_response(user_message, emotion_context)
    
    def _build_system_prompt(
        self,
        emotion_context: Optional[Dict],
        dissonance_context: Optional[Dict],
        cultural_context: Optional[Dict]
    ) -> str:
        """Build system prompt with context"""
        prompt = """You are an empathetic mental health support AI assistant for users in East Africa. 
Your role is to provide culturally-sensitive, supportive, and non-judgmental responses.

Guidelines:
- Be warm, empathetic, and understanding
- Use culturally appropriate language and examples
- Avoid medical diagnosis or prescription
- Encourage professional help when appropriate
- Be mindful of cultural context around mental health
- Respect privacy and confidentiality

"""
        
        if emotion_context:
            emotion = emotion_context.get("emotion", "neutral")
            prompt += f"Current detected emotion: {emotion}\n"
        
        if dissonance_context:
            if dissonance_context.get("dissonance_level") == "high":
                prompt += "Note: There may be a discrepancy between what the user says and how they sound. Be extra sensitive.\n"
        
        if cultural_context:
            prompt += f"Cultural context: {cultural_context.get('context', '')}\n"
        
        return prompt
    
    def _default_response(self, user_message: str, emotion_context: Optional[Dict]) -> str:
        """Default response when GPT is unavailable"""
        responses = [
            "I hear you. Thank you for sharing that with me.",
            "That sounds difficult. I'm here to listen.",
            "I understand this is challenging for you. How are you feeling right now?",
            "Thank you for trusting me with this. You're not alone.",
        ]
        
        # Simple emotion-based response selection
        if emotion_context:
            emotion = emotion_context.get("emotion", "neutral")
            if emotion in ["sad", "anxious", "fear"]:
                return "I can sense this is really hard for you. I'm here to support you. Would you like to talk more about what you're experiencing?"
        
        return responses[0]

