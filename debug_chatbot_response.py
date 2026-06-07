#!/usr/bin/env python3
"""
Debug what the chatbot send_message method returns.
"""

import json
from chatbot_module.claude_chat import ClaudeChatbot

def debug_chatbot_response():
    """Debug the chatbot response format."""
    try:
        print("🔍 Debugging chatbot response format...\n")
        
        chatbot = ClaudeChatbot()
        
        # Test with a simple message
        print("Sending simple test message...")
        response = chatbot.send_message("Hello, can you list my courses?")
        
        print("Response type:", type(response))
        print("Response keys:", list(response.keys()) if isinstance(response, dict) else "Not a dict")
        print("Full response:", response)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chatbot_response()