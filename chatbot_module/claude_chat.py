#!/usr/bin/env python3
"""
Claude-powered educational chatbot using the shared base class.
"""

import os
from typing import Optional

try:
    from langchain_anthropic import ChatAnthropic
except ImportError as e:
    print(f"Warning: Claude dependencies not available: {e}")
    ChatAnthropic = None

from chatbot_module.base_chatbot import BaseChatbot, create_educational_prompts


class ClaudeChatbot(BaseChatbot):
    """Educational chatbot using Anthropic's Claude with LangGraph tools."""
    
    def __init__(self):
        if ChatAnthropic is None:
            raise ImportError("Claude dependencies not available. Please install: pip install langchain-anthropic")
        super().__init__()
    
    def _get_api_key(self) -> Optional[str]:
        """Get Claude API key from config or environment."""
        config = self._get_config()
        
        # Try config file first
        if config and 'claude_api_chatbot_key' in config:
            return config['claude_api_chatbot_key']
        
        # Try environment variable
        return os.getenv('CLAUDE_API_KEY')
    
    def _create_model(self, api_key: str):
        """Create the Claude model instance."""
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            api_key=api_key,
            temperature=0.3
        )
    
    def get_model_type(self) -> str:
        """Return the model type identifier."""
        return "Claude Haiku + LangGraph Tools"