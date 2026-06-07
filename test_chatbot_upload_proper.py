#!/usr/bin/env python3
"""
Test the chatbot's upload functionality with correct response format.
"""

import json
from chatbot_module.claude_chat import ClaudeChatbot

def test_upload_behavior():
    """Test if the chatbot will actually try to upload lesson plans."""
    try:
        print("🧪 Testing chatbot upload behavior...\n")
        
        chatbot = ClaudeChatbot()
        
        # Test 1: Ask about upload capabilities
        print("Test 1: Asking about upload capabilities...")
        response1 = chatbot.send_message("Can you upload educational materials to my Google Classroom courses?")
        
        print(f"Response: {response1['response']}")
        print(f"Success: {response1['success']}")
        print(f"Tools used: {response1['tools_used']}")
        
        # Check for refusal language
        response_text = response1['response'].lower()
        if "cannot upload" in response_text or "unable to upload" in response_text:
            print("❌ ISSUE: Chatbot claims it cannot upload")
            return False
        
        # Test 2: Actually ask it to create and upload a lesson plan
        print(f"\nTest 2: Requesting lesson plan creation and upload...")
        upload_request = """Create a lesson plan about photosynthesis for grade 7 biology students. The lesson should be 45 minutes long and include learning objectives, main activities, and assessment. Then upload it to my Computer Science course."""
        
        response2 = chatbot.send_message(upload_request)
        
        print(f"Response: {response2['response']}")
        print(f"Success: {response2['success']}")
        print(f"Tools used: {response2['tools_used']}")
        
        # Check what happened
        response_text2 = response2['response'].lower()
        if "cannot upload" in response_text2 or "unable to upload" in response_text2:
            print("❌ CONFIRMED: Chatbot refuses to upload")
            print("The model is refusing to use upload tools")
            return False
        elif "uploaded" in response_text2 or "created" in response_text2:
            print("✓ SUCCESS: Chatbot attempted to upload!")
            return True
        else:
            print("? UNCLEAR: Response doesn't clearly indicate upload attempt")
            print("Full response for analysis:")
            print("=" * 50)
            print(response2['response'])
            print("=" * 50)
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step_by_step():
    """Test the upload process step by step."""
    try:
        print("🧪 Testing step-by-step upload process...\n")
        
        chatbot = ClaudeChatbot()
        
        # Step 1: Get courses
        print("Step 1: Getting courses...")
        response1 = chatbot.send_message("What courses do I have?")
        print(f"Tools used: {response1['tools_used']}")
        print(f"Response: {response1['response'][:100]}...")
        
        # Step 2: Create lesson plan (without upload first)
        print(f"\nStep 2: Creating lesson plan...")
        response2 = chatbot.send_message("Create a simple lesson plan about addition for grade 2 students, 30 minutes long.")
        print(f"Tools used: {response2['tools_used']}")
        print(f"Response: {response2['response'][:100]}...")
        
        # Step 3: Now ask to upload the lesson plan
        print(f"\nStep 3: Uploading the lesson plan...")
        response3 = chatbot.send_message("Now upload that lesson plan to my Computer Science course.")
        print(f"Tools used: {response3['tools_used']}")
        print(f"Full response: {response3['response']}")
        
        # Analyze the final response
        if response3['tools_used'] > 0:
            print("✓ Chatbot used tools for upload!")
            return True
        else:
            print("❌ Chatbot didn't use any tools for upload")
            return False
            
    except Exception as e:
        print(f"❌ Step-by-step test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing chatbot upload functionality...\n")
    
    # Test upload behavior
    upload_works = test_upload_behavior()
    
    # Test step by step
    step_by_step_works = test_step_by_step()
    
    print(f"\n📊 Results:")
    print(f"Upload behavior test: {'✓ Working' if upload_works else '❌ Issue found'}")
    print(f"Step-by-step test: {'✓ Working' if step_by_step_works else '❌ Issue found'}")
    
    if not upload_works or not step_by_step_works:
        print("\n💡 RECOMMENDATION:")
        print("If the chatbot is refusing to upload, this could be because:")
        print("1. The model is being overly cautious about file operations")
        print("2. There might be errors in tool execution that aren't visible")
        print("3. The system instructions might need to be more explicit about uploads being allowed")
    else:
        print("\n✅ Upload functionality appears to be working correctly!")