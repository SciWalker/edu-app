#!/usr/bin/env python3
"""
Quiz generation tools for LangGraph educational agent.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool

# Add parent directories to path for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))


@tool
def generate_quiz(content: str, topic: str = "General Knowledge", num_questions: int = 5) -> str:
    """Generate quiz questions from educational content.
    
    Args:
        content: The educational content to create quiz from
        topic: The topic/subject of the content
        num_questions: Number of questions to generate (default: 5)
        
    Returns:
        JSON string with generated quiz questions and answers
    """
    try:
        from src.generate_quiz import generate_quiz_with_gemini
        import json
        
        # Create lesson plan structure for quiz generation
        lesson_plan = {
            'topic': topic,
            'content': content,
            'number_of_questions': num_questions,
            'response_type': 'multiple_choice_question'
        }
        
        # Generate quiz using existing quiz generation logic
        quiz_data = generate_quiz_with_gemini(lesson_plan)
        
        return json.dumps({
            "success": True,
            "quiz": quiz_data,
            "topic": topic,
            "num_questions": len(quiz_data.get('questions', [])),
            "message": f"Generated {len(quiz_data.get('questions', []))} quiz questions for {topic}"
        }, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to generate quiz"
        }, indent=2)


@tool
def create_classroom_quiz(course_id: str, quiz_data: str, title: str = None) -> str:
    """Create and upload a quiz to Google Classroom.
    
    Args:
        course_id: The ID of the Google Classroom course
        quiz_data: JSON string containing the quiz questions and answers
        title: Optional title for the quiz (will use quiz title if not provided)
        
    Returns:
        Success/failure message with quiz upload details
    """
    try:
        from ocr_module.classroom_uploader import OCRClassroomUploader
        import json
        
        # Parse quiz data
        quiz_info = json.loads(quiz_data)
        
        # Extract quiz from the data structure
        if "quiz" in quiz_info:
            quiz = quiz_info["quiz"]
        else:
            quiz = quiz_info
        
        # Prepare quiz data for classroom upload
        classroom_data = {
            "structured_data": {
                "title": title or quiz.get("title", "Generated Quiz"),
                "questions": quiz.get("questions", []),
                "quiz_type": "multiple_choice",
                "content_source": "ai_generated"
            },
            "confidence_score": 0.9,
            "extraction_type": "quiz"
        }
        
        # Upload to Google Classroom
        uploader = OCRClassroomUploader()
        result = uploader.upload_to_classroom(
            course_id=course_id,
            ocr_data=classroom_data,
            assignment_type="quiz"
        )
        
        return json.dumps({
            "success": result.get("success", False),
            "quiz_title": result.get("title", "Unknown"),
            "course_id": course_id,
            "num_questions": len(quiz.get("questions", [])),
            "message": f"Quiz uploaded to Google Classroom: {result.get('title', 'Unknown')}"
        }, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to upload quiz to Google Classroom"
        }, indent=2)


@tool
def generate_lesson_quiz(lesson_content: str, course_id: str, topic: str = "Lesson Quiz") -> str:
    """Generate a quiz from lesson content and upload it directly to Google Classroom.
    
    Args:
        lesson_content: The lesson content to create quiz from
        course_id: The ID of the Google Classroom course
        topic: The topic/title for the quiz
        
    Returns:
        Complete workflow result with quiz generation and upload status
    """
    try:
        import json
        
        # Step 1: Generate quiz
        quiz_result = generate_quiz(lesson_content, topic, 5)
        quiz_data = json.loads(quiz_result)
        
        if not quiz_data.get("success"):
            return quiz_result  # Return the error from quiz generation
        
        # Step 2: Upload to classroom
        upload_result = create_classroom_quiz(
            course_id=course_id,
            quiz_data=json.dumps(quiz_data["quiz"]),
            title=f"Quiz: {topic}"
        )
        
        upload_data = json.loads(upload_result)
        
        return json.dumps({
            "success": upload_data.get("success", False),
            "quiz_generated": True,
            "quiz_uploaded": upload_data.get("success", False),
            "quiz_title": upload_data.get("quiz_title", topic),
            "num_questions": quiz_data.get("num_questions", 0),
            "course_id": course_id,
            "message": f"Complete workflow: Generated and uploaded quiz '{topic}' with {quiz_data.get('num_questions', 0)} questions"
        }, indent=2)
        
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to complete lesson quiz workflow"
        }, indent=2)