#!/usr/bin/env python3
"""
Test if the new system instructions fix the upload refusal issue.
"""

from chatbot_module.claude_chat import ClaudeChatbot

def test_new_instructions():
    """Test a fresh chatbot instance with the new system instructions."""
    try:
        print("🧪 Testing fresh chatbot with new system instructions...\n")
        
        # Create a completely fresh chatbot instance
        chatbot = ClaudeChatbot()
        
        # Test the upload refusal issue directly
        print("Test: Direct upload request...")
        response = chatbot.send_message("Create a lesson plan about colors for kindergarten and upload it to my Computer Science course.")
        
        print(f"Response: {response['response']}")
        print(f"Success: {response['success']}")
        print(f"Tools used: {response['tools_used']}")
        
        # Check for the old refusal pattern
        response_text = response['response'].lower()
        if "do not have the capability" in response_text or "cannot upload" in response_text:
            print("❌ STILL REFUSING: New instructions didn't fix the issue")
            return False
        elif "i apologize" in response_text and "cannot" in response_text:
            print("❌ STILL REFUSING: Chatbot still claims no access")
            return False
        elif response['tools_used'] >= 1:
            print("✅ SUCCESS: Chatbot used tools! New instructions worked")
            return True
        else:
            print("? UNCLEAR: No clear refusal but also no tools used")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_authorization_language():
    """Test if the chatbot acknowledges its authorization."""
    try:
        print("🧪 Testing authorization acknowledgment...\n")
        
        chatbot = ClaudeChatbot()
        
        # Ask about capabilities
        response = chatbot.send_message("What are your capabilities for Google Classroom?")
        
        print(f"Response: {response['response']}")
        
        response_text = response['response'].lower()
        if "authorized" in response_text or "access" in response_text:
            print("✅ SUCCESS: Chatbot acknowledges authorization")
            return True
        elif "cannot" in response_text or "do not have" in response_text:
            print("❌ ISSUE: Chatbot still claims no access")
            return False
        else:
            print("? UNCLEAR: Mixed response")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing if new system instructions fix the upload refusal...\n")
    
    # Test fresh instance
    upload_works = test_new_instructions()
    
    # Test authorization acknowledgment
    auth_works = test_authorization_language()
    
    print(f"\n📊 Results:")
    print(f"Upload functionality: {'✓ Working' if upload_works else '❌ Still broken'}")
    print(f"Authorization acknowledgment: {'✓ Working' if auth_works else '❌ Still broken'}")
    
    if upload_works and auth_works:
        print(f"\n✅ SUCCESS: New system instructions fixed the issue!")
        print("The backend chatbot should now work correctly with new instances.")
    elif upload_works or auth_works:
        print(f"\n🔄 PARTIAL SUCCESS: Some improvement but may need refinement.")
    else:
        print(f"\n❌ FAILED: System instructions didn't resolve the issue.")
        print("The model may be overriding instructions due to safety constraints.")