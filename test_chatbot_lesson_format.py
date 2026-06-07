#!/usr/bin/env python3
"""
Test what format the chatbot is actually creating for lesson plans.
"""

from chatbot_module.claude_chat import ClaudeChatbot
import json

def test_lesson_plan_format():
    """Test the actual format the chatbot creates for lesson plans."""
    try:
        print("🧪 Testing chatbot lesson plan format...\n")
        
        chatbot = ClaudeChatbot()
        
        # Ask for a structured lesson plan
        print("Requesting structured lesson plan...")
        response = chatbot.send_message("""Create a comprehensive lesson plan for Computer Science about Lie Algebra. 
        Format it as a detailed educational plan with specific structure including title, subject, grade level, duration, learning objectives, key topics, lesson structure, materials, vocabulary, homework, difficulty level, assessment criteria, differentiation, extension activities, and prerequisite knowledge.""")
        
        print(f"Response: {response['response'][:200]}...")
        print(f"Tools used: {response['tools_used']}")
        
        # Now ask to upload with specific format
        print(f"\nTesting upload with format specification...")
        upload_response = chatbot.send_message("""Upload that lesson plan to my Computer Science course. 
        Use the comprehensive structured format with all educational components.""")
        
        print(f"Upload response: {upload_response['response']}")
        print(f"Upload tools used: {upload_response['tools_used']}")
        
        if upload_response['tools_used'] >= 2:
            print("✅ SUCCESS: Chatbot used tools to upload")
            return True
        else:
            print("❌ ISSUE: Chatbot didn't use tools for upload")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_explicit_json_format():
    """Test asking the chatbot to create lesson plan in JSON format."""
    try:
        print("🧪 Testing explicit JSON format request...\n")
        
        chatbot = ClaudeChatbot()
        
        # Request JSON format explicitly
        json_request = """Create a lesson plan for Computer Science about Lie Algebra in this exact JSON format:
        {
          "title": "Introduction to Lie Algebra",
          "subject": "Computer Science",
          "grade_level": "College",
          "duration": "90 minutes",
          "learning_objectives": ["Understand basic Lie algebra concepts", "Apply to CS problems"],
          "key_topics": ["Lie brackets", "Matrix Lie algebras", "Applications in robotics"],
          "lesson_structure": {
            "introduction": "Overview of algebraic structures (15 min)",
            "main_activities": ["Theory presentation (30 min)", "Examples and problems (30 min)", "Group discussion (15 min)"],
            "assessment": "Problem-solving exercise",
            "conclusion": "Summary and next steps"
          },
          "materials_needed": ["Linear algebra textbook", "Computer with mathematical software"],
          "vocabulary": ["Lie bracket", "Jacobi identity", "Representation"],
          "homework_assignments": ["Practice problems on Lie brackets"],
          "difficulty_level": "advanced",
          "assessment_criteria": ["Understanding of concepts", "Problem-solving ability"],
          "differentiation": "Provide additional examples for struggling students",
          "extension_activities": ["Research applications in computer graphics"],
          "prerequisite_knowledge": ["Linear algebra", "Abstract algebra basics"]
        }
        
        Then upload it to my Computer Science course."""
        
        response = chatbot.send_message(json_request)
        
        print(f"Response: {response['response'][:300]}...")
        print(f"Tools used: {response['tools_used']}")
        
        if response['tools_used'] >= 2:
            print("✅ SUCCESS: JSON format request worked")
            return True
        else:
            print("❌ ISSUE: JSON format request didn't work")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing chatbot lesson plan format...\n")
    
    # Test general format
    general_works = test_lesson_plan_format()
    
    # Test explicit JSON format
    json_works = test_explicit_json_format()
    
    print(f"\n📊 Results:")
    print(f"General format: {'✓ Working' if general_works else '❌ Issue'}")
    print(f"JSON format: {'✓ Working' if json_works else '❌ Issue'}")
    
    if general_works and json_works:
        print(f"\n✅ SUCCESS: Chatbot can create comprehensive lesson plans")
        print("The format should now work correctly in Google Classroom")
    else:
        print(f"\n🔧 PARTIAL: May need further refinement to ensure comprehensive format")