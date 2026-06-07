#!/usr/bin/env python3
"""
LangGraph tools for Google Classroom management.
Uses existing classroom_handler functions to provide tool interface for chatbot.
"""

from langchain_core.tools import tool
import json
import classroom_handler


@tool
def invite_student_to_course(course_id: str, student_email: str) -> str:
    """Invite a student to join a Google Classroom course.
    
    Args:
        course_id: The ID of the course to invite the student to
        student_email: Email address of the student to invite
        
    Returns:
        JSON string with invitation status and details
    """
    try:
        result = classroom_handler.invite_student(course_id, student_email)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error inviting student: {str(e)}",
            "course_id": course_id,
            "student_email": student_email
        }, indent=2)


@tool
def invite_multiple_students_to_courses(students_data: str) -> str:
    """Invite multiple students to Google Classroom courses.
    
    Args:
        students_data: JSON string containing list of student data.
                      Each student should have 'email', 'course_id', and optionally 'first_name', 'last_name'
        
    Returns:
        JSON string with invitation results summary and individual results
    """
    try:
        # Parse the students data
        students_list = json.loads(students_data)
        
        result = classroom_handler.invite_multiple_students(students_list)
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error inviting students: {str(e)}"
        }, indent=2)


@tool  
def create_quiz_from_data(course_id: str, quiz_title: str, quiz_questions: str, due_date: str = None) -> str:
    """Create a quiz assignment in Google Classroom from provided data.
    
    Args:
        course_id: The ID of the course to create the quiz in
        quiz_title: Title of the quiz
        quiz_questions: JSON string containing quiz questions data
        due_date: Optional due date in ISO format (e.g., "2024-12-25T23:59:00")
        
    Returns:
        JSON string with quiz creation status and details
    """
    try:
        # Parse quiz questions
        questions_data = json.loads(quiz_questions)
        
        # Create quiz data structure
        quiz_data = {
            "title": quiz_title,
            "questions": questions_data
        }
        
        result = classroom_handler.create_quiz_assignment(course_id, quiz_data, due_date)
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid JSON format for quiz questions: {str(e)}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error creating quiz: {str(e)}"
        }, indent=2)


@tool
def upload_quiz_from_file(course_id: str, quiz_file_path: str = "../data/quiz.json", due_date: str = None) -> str:
    """Load quiz from JSON file and create assignment in Google Classroom.
    
    Args:
        course_id: The ID of the course to create the assignment in
        quiz_file_path: Path to the quiz JSON file (relative to src/ directory)
        due_date: Optional due date in ISO format
        
    Returns:
        JSON string with quiz creation status and details
    """
    try:
        result = classroom_handler.upload_quiz_from_file(course_id, quiz_file_path, due_date)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error uploading quiz from file: {str(e)}"
        }, indent=2)


@tool
def get_course_students(course_id: str) -> str:
    """Get all students enrolled in a specific Google Classroom course.
    
    Args:
        course_id: The ID of the course to get students for
        
    Returns:
        JSON string with student roster
    """
    try:
        # Get the classroom service
        service = classroom_handler.get_classroom_service()
        if not service:
            return json.dumps({
                "success": False,
                "error": "Failed to connect to Google Classroom service"
            }, indent=2)
        
        # Get course students
        students_result = service.courses().students().list(courseId=course_id).execute()
        students = students_result.get('students', [])
        
        # Format student data
        formatted_students = []
        for student in students:
            profile = student.get('profile', {})
            formatted_students.append({
                "user_id": student.get('userId'),
                "course_id": student.get('courseId'),
                "full_name": profile.get('name', {}).get('fullName', ''),
                "given_name": profile.get('name', {}).get('givenName', ''),
                "family_name": profile.get('name', {}).get('familyName', ''),
                "email_address": profile.get('emailAddress', ''),
                "photo_url": profile.get('photoUrl', '')
            })
        
        return json.dumps({
            "success": True,
            "course_id": course_id,
            "total_students": len(formatted_students),
            "students": formatted_students
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error getting course students: {str(e)}",
            "course_id": course_id
        }, indent=2)


@tool
def create_new_course(course_name: str, section: str = "", description: str = "", room: str = "") -> str:
    """Create a new Google Classroom course.
    
    Args:
        course_name: Name of the course (e.g., "Mathematics 101", "Biology Advanced")
        section: Section identifier (optional, e.g., "A", "Period 1")
        description: Course description (optional)
        room: Room location (optional, e.g., "Room 101")
        
    Returns:
        JSON string with course creation status and details
    """
    try:
        result = classroom_handler.create_course(course_name, section, description, room)
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error creating course: {str(e)}",
            "course_name": course_name
        }, indent=2)


# List of all tools for easy import
CLASSROOM_TOOLS = [
    invite_student_to_course,
    invite_multiple_students_to_courses, 
    create_quiz_from_data,
    upload_quiz_from_file,
    get_course_students,
    create_new_course
]