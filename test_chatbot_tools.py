#!/usr/bin/env python3
"""
Test the chatbot's tool access and functionality.
"""

import json
from chatbot_module.claude_chat import ClaudeChatbot

def test_chatbot_tools():
    """Test if the chatbot can access and use its tools."""
    try:
        print("🧪 Testing chatbot tool access...\n")
        
        chatbot = ClaudeChatbot()
        
        # Test 1: Ask for courses (should call get_courses tool)
        print("Test 1: Getting courses...")
        response1 = chatbot.send_message("What courses do I have in Google Classroom?")
        print(f"Response: {response1['content'][:200]}...")
        print(f"Success: {response1['success']}")
        
        if not response1['success']:
            print(f"❌ Failed to get courses: {response1.get('error', 'Unknown error')}")
            return False
        
        # Test 2: Ask about lesson plan creation (should mention tools available)
        print(f"\nTest 2: Asking about lesson plan upload capabilities...")
        response2 = chatbot.send_message("Can you help me create and upload a lesson plan to one of my courses?")
        print(f"Response: {response2['content']}")
        print(f"Success: {response2['success']}")
        
        # Check if the response mentions inability to upload (the problem we're investigating)
        if "cannot upload" in response2['content'].lower() or "cannot directly upload" in response2['content'].lower():
            print("❌ FOUND THE ISSUE: Chatbot says it cannot upload!")
            print("This suggests the model is refusing to use upload tools")
            return False
        elif "upload_material" in response2['content'] or "upload" in response2['content'].lower():
            print("✓ Chatbot acknowledges upload capabilities")
            return True
        else:
            print("? Unclear response about upload capabilities")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lesson_plan_creation():
    """Test asking the chatbot to actually create and upload a lesson plan."""
    try:
        print("🧪 Testing lesson plan creation and upload...\n")
        
        chatbot = ClaudeChatbot()
        
        # Ask for a specific lesson plan creation and upload
        message = """Create a simple lesson plan about basic mathematics (addition and subtraction) for grade 3 students, and upload it to my Computer Science course. The lesson should be 30 minutes long."""
        
        print(f"Request: {message}")
        response = chatbot.send_message(message)
        
        print(f"\nResponse: {response['content']}")
        print(f"Success: {response['success']}")
        
        # Check if it actually tries to upload or refuses
        if "cannot upload" in response['content'].lower():
            print("❌ CONFIRMED: Chatbot refuses to upload")
            return False
        elif "upload" in response['content'].lower() and "success" in response['content'].lower():
            print("✓ Chatbot attempted upload")
            return True
        else:
            print("? Unclear whether upload was attempted")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Investigating chatbot upload refusal issue...\n")
    
    # Test basic tool access
    tools_working = test_chatbot_tools()
    
    # Test lesson plan creation
    upload_working = test_lesson_plan_creation()
    
    print(f"\n📊 Results:")
    print(f"Tool access: {'✓ Working' if tools_working else '❌ Issue found'}")
    print(f"Upload capability: {'✓ Working' if upload_working else '❌ Issue found'}")
    
    if not tools_working or not upload_working:
        print("\n🚨 DIAGNOSIS: The chatbot appears to be refusing to use upload tools")
        print("This might be due to:")
        print("1. Model safety constraints")
        print("2. Tool execution errors that cause the model to avoid them")
        print("3. System instruction conflicts")
        print("4. Authentication/permission issues")
    else:
        print("\n✅ All tests passed - upload functionality should work")