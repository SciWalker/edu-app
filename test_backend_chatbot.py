#!/usr/bin/env python3
"""
Test the actual backend chatbot to see why it refuses uploads.
"""

import requests
import json

def test_backend_chatbot():
    """Test the chatbot through the actual backend API."""
    backend_url = "http://localhost:5000"
    
    try:
        # Test 1: Check status
        print("🧪 Testing backend chatbot API...\n")
        
        status_response = requests.get(f"{backend_url}/api/chatbot/status")
        status = status_response.json()
        print(f"Current chatbot: {status['current_chatbot']}")
        print(f"Available chatbots: {status['available_chatbots']}")
        
        # Test 2: Ask about upload capability
        print(f"\nTest 1: Asking about upload capabilities...")
        message1 = {
            "message": "Can you upload lesson plans to my Google Classroom courses?",
            "user_id": "test_user"
        }
        
        response1 = requests.post(f"{backend_url}/api/chatbot/message", json=message1)
        result1 = response1.json()
        
        print(f"Success: {result1.get('success', False)}")
        print(f"Response: {result1.get('response', 'No response')}")
        print(f"Tools used: {result1.get('tools_used', 0)}")
        
        # Test 3: Direct upload request
        print(f"\nTest 2: Direct upload request...")
        message2 = {
            "message": "Create a simple lesson plan about fractions for grade 4 students and upload it to my Computer Science course.",
            "user_id": "test_user"
        }
        
        response2 = requests.post(f"{backend_url}/api/chatbot/message", json=message2)
        result2 = response2.json()
        
        print(f"Success: {result2.get('success', False)}")
        print(f"Response: {result2.get('response', 'No response')}")
        print(f"Tools used: {result2.get('tools_used', 0)}")
        
        # Analyze responses
        response1_text = result1.get('response', '').lower()
        response2_text = result2.get('response', '').lower()
        
        print(f"\n📊 Analysis:")
        
        if "cannot upload" in response1_text or "cannot upload" in response2_text:
            print("❌ CONFIRMED: Backend chatbot refuses uploads")
            return False
        elif "do not have" in response1_text or "do not have" in response2_text:
            print("❌ CONFIRMED: Backend chatbot claims no access")
            return False
        elif result2.get('tools_used', 0) >= 2:
            print("✅ SUCCESS: Backend chatbot attempts uploads")
            return True
        else:
            print("? UNCLEAR: Mixed results")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_switch_chatbot():
    """Test switching between chatbot types to see if one works better."""
    backend_url = "http://localhost:5000"
    
    try:
        print("🧪 Testing chatbot switching...\n")
        
        # Test with Gemini first
        print("Switching to Gemini...")
        switch_request = {"chatbot_type": "langgraph_gemini"}
        switch_response = requests.post(f"{backend_url}/api/chatbot/switch", json=switch_request)
        print(f"Switch result: {switch_response.json()}")
        
        # Test upload with Gemini
        message = {
            "message": "Upload a lesson plan about addition to my Computer Science course",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{backend_url}/api/chatbot/message", json=message)
        result = response.json()
        
        print(f"Gemini response: {result.get('response', '')[:100]}...")
        print(f"Gemini tools used: {result.get('tools_used', 0)}")
        
        gemini_refuses = "cannot upload" in result.get('response', '').lower()
        
        # Test with Claude
        print(f"\nSwitching to Claude...")
        switch_request = {"chatbot_type": "langgraph_claude"}
        switch_response = requests.post(f"{backend_url}/api/chatbot/switch", json=switch_request)
        print(f"Switch result: {switch_response.json()}")
        
        # Test upload with Claude
        response = requests.post(f"{backend_url}/api/chatbot/message", json=message)
        result = response.json()
        
        print(f"Claude response: {result.get('response', '')[:100]}...")
        print(f"Claude tools used: {result.get('tools_used', 0)}")
        
        claude_refuses = "cannot upload" in result.get('response', '').lower()
        
        print(f"\n📊 Comparison:")
        print(f"Gemini refuses upload: {'Yes' if gemini_refuses else 'No'}")
        print(f"Claude refuses upload: {'Yes' if claude_refuses else 'No'}")
        
        if gemini_refuses and claude_refuses:
            print("❌ ISSUE: Both chatbots refuse uploads in backend")
            return False
        elif not gemini_refuses or not claude_refuses:
            print("✅ SUCCESS: At least one chatbot works")
            return True
        else:
            print("? UNCLEAR: Mixed results")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot switching test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing backend chatbot upload behavior...\n")
    
    # Test current backend
    backend_works = test_backend_chatbot()
    
    # Test switching
    switching_works = test_switch_chatbot()
    
    print(f"\n🎯 CONCLUSION:")
    if backend_works or switching_works:
        print("✅ Backend chatbot can upload (at least sometimes)")
        print("The refusal might be context-dependent or intermittent")
    else:
        print("❌ Backend chatbot consistently refuses uploads")
        print("This suggests a difference between test environment and backend environment")
        print("\n💡 POSSIBLE CAUSES:")
        print("1. Different system instructions between direct test and backend")
        print("2. Tool initialization issues in backend environment") 
        print("3. Authentication problems in backend vs test")
        print("4. Model safety constraints triggered by specific conversation context")