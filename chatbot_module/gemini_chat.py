#!/usr/bin/env python3
"""
Gemini-powered educational chatbot using the shared base class.
"""

import os
from typing import Optional

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    print(f"Warning: Gemini dependencies not available: {e}")
    ChatGoogleGenerativeAI = None

from chatbot_module.base_chatbot import BaseChatbot, create_educational_prompts


class GeminiChatbot(BaseChatbot):
    """Educational chatbot using Google's Gemini AI with LangGraph tools."""
    
    def __init__(self):
        if ChatGoogleGenerativeAI is None:
            raise ImportError("Gemini dependencies not available. Please install: pip install langchain-google-genai")
        super().__init__()
    
    def _get_api_key(self) -> Optional[str]:
        """Get Gemini API key from config or environment."""
        config = self._get_config()
        
        # Try config file first
        if config and 'google_ai_studio_api_key' in config:
            return config['google_ai_studio_api_key']
        
        # Try environment variable
        return os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    
    def _create_model(self, api_key: str):
        """Create the Gemini model instance."""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=api_key,
            temperature=0.3
        )
    
    def get_model_type(self) -> str:
        """Return the model type identifier."""
        return "Gemini 1.5 Pro + LangGraph Tools"