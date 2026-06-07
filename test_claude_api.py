#!/usr/bin/env python3
"""
Test script to verify Claude API connection and key.
"""

import yaml
import os

try:
    import anthropic
    print("✓ anthropic package is installed")
except ImportError:
    print("✗ anthropic package not found. Install with: pip install anthropic")
    exit(1)

# Load configuration
try:
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    print("✓ config.yml loaded successfully")
except Exception as e:
    print(f"✗ Failed to load config.yml: {e}")
    exit(1)

# Get Claude API key
claude_api_key = (
    config.get("claude_api_chatbot_key") or 
    os.getenv("CLAUDE_API_KEY") or
    os.getenv("ANTHROPIC_API_KEY")
)

if not claude_api_key:
    print("✗ Claude API key not found in config.yml or environment variables")
    exit(1)

print("✓ Claude API key found")

# Test Claude API connection
try:
    client = anthropic.Anthropic(api_key=claude_api_key)
    print("✓ Claude client created successfully")
    
    # Test a simple API call
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello! Just testing the API. Please respond with 'API test successful'."}]
    )
    
    response_text = response.content[0].text.strip()
    print(f"✓ Claude API call successful!")
    print(f"Response: {response_text}")
    
except Exception as e:
    print(f"✗ Claude API test failed: {type(e).__name__}: {str(e)}")
    
    if "connection" in str(e).lower():
        print("  - This appears to be a network/connection issue")
        print("  - Check your internet connection")
        print("  - Verify firewall settings allow HTTPS to api.anthropic.com")
    elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
        print("  - This appears to be an API key issue")
        print("  - Verify your claude_api_chatbot_key in config.yml is correct")
        print("  - Check that the API key has proper permissions")
    elif "rate" in str(e).lower():
        print("  - This appears to be a rate limiting issue")
        print("  - Wait a moment and try again")
    
    exit(1)

print("\n🎉 All tests passed! Claude API is working correctly.")