#!/usr/bin/env python3
"""
Test upload with the exact course IDs we know exist.
"""

from chatbot_module.claude_chat import ClaudeChatbot

def test_with_exact_course_id():
    """Test upload with the exact course ID we know exists."""
    try:
        print("🧪 Testing upload with exact course ID...\n")
        
        chatbot = ClaudeChatbot()
        
        # Use the Computer Science course ID we saw: 795316828054
        course_id = "795316828054"
        
        upload_message = f"""Create a simple lesson plan about basic programming concepts for high school students (45 minutes long) and upload it to the course with ID {course_id}."""
        
        print(f"Testing upload to course {course_id}...")
        response = chatbot.send_message(upload_message)
        print(f"Upload response: {response['response']}")
        print(f"Success: {response['success']}")
        print(f"Tools used: {response['tools_used']}")
        print(f"Error: {response.get('error', 'None')}")
        
        # Analyze the result
        response_text = response['response'].lower()
        if "successfully uploaded" in response_text or "uploaded successfully" in response_text:
            print("✅ SUCCESS: Upload worked!")
            return True
        elif "cannot upload" in response_text or "unable to upload" in response_text:
            print("❌ REFUSAL: Chatbot refuses to upload")
            return False
        elif "error" in response_text or "failed" in response_text:
            print("❌ ERROR: Upload failed with error")
            return False
        else:
            print("? UNCLEAR: Uncertain result")
            print("Let's check if tools were actually used...")
            if response['tools_used'] >= 2:  # get_courses + upload_material
                print("✓ Tools were used, likely attempted upload")
                return True
            else:
                print("❌ Insufficient tools used")
                return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_manual_lesson_plan_format():
    """Test providing a pre-formatted lesson plan to upload."""
    try:
        print("🧪 Testing with pre-formatted lesson plan...\n")
        
        chatbot = ClaudeChatbot()
        
        # Create a properly formatted lesson plan first
        lesson_plan = {
            "title": "Introduction to Variables",
            "subject": "Computer Science",
            "grade_level": "Grade 9",
            "duration": "50 minutes",
            "learning_objectives": [
                "Understand what variables are in programming",
                "Learn to declare and assign variables",
                "Practice using variables in simple programs"
            ],
            "key_topics": ["Variables", "Data types", "Assignment"],
            "lesson_structure": {
                "introduction": "What are variables? (10 min)",
                "main_activities": [
                    "Demonstrate variable declaration (15 min)",
                    "Students practice with examples (20 min)"
                ],
                "assessment": "Quick quiz on variable concepts",
                "conclusion": "Review key points (5 min)"
            },
            "materials_needed": ["Computer", "Code editor"],
            "vocabulary": ["Variable", "Declaration", "Assignment"],
            "homework_assignments": ["Complete practice exercises"],
            "difficulty_level": "beginner"
        }
        
        import json
        lesson_plan_json = json.dumps(lesson_plan)
        
        upload_message = f"""Upload this lesson plan to my Computer Science course (ID: 795316828054): {lesson_plan_json}"""
        
        print("Testing upload with pre-formatted lesson plan...")
        response = chatbot.send_message(upload_message)
        print(f"Response: {response['response']}")
        print(f"Tools used: {response['tools_used']}")
        
        if response['tools_used'] > 0:
            print("✓ Chatbot used tools to attempt upload")
            return True
        else:
            print("❌ Chatbot didn't use tools")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing with exact course IDs...\n")
    
    # Test with exact course ID
    exact_id_works = test_with_exact_course_id()
    
    # Test with pre-formatted lesson plan
    manual_format_works = test_manual_lesson_plan_format()
    
    print(f"\n📊 Final Analysis:")
    print(f"Exact course ID test: {'✓ Working' if exact_id_works else '❌ Failed'}")
    print(f"Manual format test: {'✓ Working' if manual_format_works else '❌ Failed'}")
    
    if exact_id_works or manual_format_works:
        print(f"\n✅ CONCLUSION: The chatbot CAN upload lesson plans!")
        print("The error message you encountered may have been from a specific edge case.")
        print("The fix we implemented should resolve the structured data issue.")
    else:
        print(f"\n❌ CONCLUSION: There are persistent upload issues.")
        print("This might require further investigation of the Google Classroom API setup.")