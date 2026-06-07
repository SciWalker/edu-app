#!/usr/bin/env python3
"""
Test what happens when the upload_material tool encounters specific errors.
"""

import json
from chatbot_module.claude_chat import ClaudeChatbot

def test_upload_with_real_course():
    """Test upload with a real course ID to see if that's the issue."""
    try:
        print("🧪 Testing upload with real course ID...\n")
        
        chatbot = ClaudeChatbot()
        
        # First get the actual course IDs
        print("Getting real course information...")
        response1 = chatbot.send_message("List my Google Classroom courses with their IDs")
        print(f"Course info: {response1['response']}")
        
        # Extract course ID (look for a pattern like numeric ID)
        import re
        course_id_match = re.search(r'"id":\s*"([^"]+)"', response1['response'])
        if not course_id_match:
            # Try different pattern
            course_id_match = re.search(r'ID:\s*([^\s,]+)', response1['response'])
        
        if course_id_match:
            course_id = course_id_match.group(1)
            print(f"Found course ID: {course_id}")
            
            # Now try to upload to this specific course
            upload_message = f"""Create a simple lesson plan about basic shapes for kindergarten students (20 minutes long) and upload it to the course with ID {course_id}."""
            
            print(f"\nTesting upload to course {course_id}...")
            response2 = chatbot.send_message(upload_message)
            print(f"Upload response: {response2['response']}")
            print(f"Tools used: {response2['tools_used']}")
            
            if "successfully uploaded" in response2['response'].lower():
                print("✅ SUCCESS: Upload worked with real course ID!")
                return True
            elif "error" in response2['response'].lower() or "issue" in response2['response'].lower():
                print("❌ ISSUE: Upload failed even with real course ID")
                print("This suggests there might be permission or API issues")
                return False
            else:
                print("? UNCLEAR: Uncertain upload result")
                return False
        else:
            print("❌ Could not extract course ID from response")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_chatbot_error_handling():
    """Test how the chatbot responds to upload errors."""
    try:
        print("🧪 Testing chatbot error handling...\n")
        
        chatbot = ClaudeChatbot()
        
        # Try to upload to an invalid course ID to see how it handles errors
        error_message = """Create a lesson plan about colors for preschoolers and upload it to course ID "invalid_course_123"."""
        
        print("Testing with invalid course ID...")
        response = chatbot.send_message(error_message)
        print(f"Error handling response: {response['response']}")
        print(f"Tools used: {response['tools_used']}")
        
        # Check how it handles the error
        response_text = response['response'].lower()
        if "cannot upload" in response_text or "don't have access" in response_text:
            print("✓ Chatbot properly handles upload errors by explaining limitations")
            return True
        elif "error" in response_text or "issue" in response_text:
            print("✓ Chatbot reports upload errors appropriately")
            return True
        else:
            print("? Unclear error handling")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing specific upload scenarios...\n")
    
    # Test with real course
    real_course_works = test_upload_with_real_course()
    
    # Test error handling
    error_handling_works = test_chatbot_error_handling()
    
    print(f"\n📊 Analysis:")
    print(f"Real course upload: {'✓ Working' if real_course_works else '❌ Issue'}")
    print(f"Error handling: {'✓ Working' if error_handling_works else '❌ Issue'}")
    
    print(f"\n🔍 CONCLUSION:")
    if real_course_works:
        print("✅ The chatbot CAN upload lesson plans successfully!")
        print("The error message you saw might be from a specific failure case.")
    else:
        print("❌ There appear to be persistent issues with uploads.")
        print("This could be due to Google Classroom API permissions or authentication.")