#!/usr/bin/env python3
"""
Google Classroom tools for LangGraph educational agent.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

# Add parent directories to path for imports
parent_dir = Path(__file__).parent.parent.parent
src_dir = parent_dir / "src"
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))


@tool 
def get_courses() -> str:
    """Get all Google Classroom courses for the teacher.
    
    Returns:
        JSON string with course information including names, IDs, sections, and status.
    """
    try:
        import classroom_handler
        courses = classroom_handler.list_courses()
        
        if not courses:
            return "No Google Classroom courses found. The teacher may not have any active courses or there may be an authentication issue."
        
        course_list = []
        for course in courses:
            course_info = {
                "id": course.get("id", ""),
                "name": course.get("name", "Unnamed Course"),
                "section": course.get("section", ""),
                "description": course.get("description", ""),
                "courseState": course.get("courseState", "UNKNOWN"),
                "link": course.get("alternateLink", ""),
                "teacherFolder": course.get("teacherFolder", {}).get("title", "")
            }
            course_list.append(course_info)
        
        import json
        return json.dumps({
            "total_courses": len(course_list),
            "courses": course_list
        }, indent=2)
        
    except Exception as e:
        return f"Error fetching courses: {str(e)}"


@tool  
def get_course_details(course_id: str) -> str:
    """Get detailed information about a specific Google Classroom course.
    
    Args:
        course_id: The ID of the course to get details for
        
    Returns:
        JSON string with detailed course information
    """
    try:
        import classroom_handler
        # For now, we'll get all courses and filter
        courses = classroom_handler.list_courses()
        
        target_course = None
        for course in courses:
            if course.get("id") == course_id:
                target_course = course
                break
        
        if not target_course:
            return f"Course with ID {course_id} not found."
        
        import json
        return json.dumps({
            "course": target_course,
            "message": f"Found course: {target_course.get('name', 'Unknown')}"
        }, indent=2)
        
    except Exception as e:
        return f"Error getting course details: {str(e)}"


@tool
def create_assignment(course_id: str, title: str, description: str, assignment_type: str = "assignment") -> str:
    """Create an assignment in Google Classroom.
    
    Args:
        course_id: The ID of the course to create assignment in
        title: Title of the assignment
        description: Description of the assignment  
        assignment_type: Type of assignment (assignment, quiz, material)
        
    Returns:
        Success/failure message with assignment details
    """
    try:
        from ocr_module.classroom_uploader import OCRClassroomUploader
        
        uploader = OCRClassroomUploader()
        
        # Create assignment data structure
        assignment_data = {
            "structured_data": {
                "title": title,
                "description": description,
                "questions": [] if assignment_type == "quiz" else None
            },
            "confidence_score": 1.0,
            "extraction_type": assignment_type
        }
        
        result = uploader.upload_to_classroom(
            course_id=course_id,
            ocr_data=assignment_data,
            assignment_type=assignment_type
        )
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error creating assignment: {str(e)}"


@tool
def upload_material(course_id: str, material_data: str) -> str:
    """Upload educational material to Google Classroom.
    
    Args:
        course_id: The ID of the course to upload to
        material_data: JSON string containing the material information
        
    Returns:
        Success/failure message with upload details
    """
    try:
        from ocr_module.classroom_uploader import OCRClassroomUploader
        import json
        
        # Parse material data
        material_info = json.loads(material_data)
        
        # Check if this is already in OCR format or needs to be wrapped
        if "structured_data" not in material_info:
            # This is a raw lesson plan from chatbot, wrap it in OCR format
            ocr_formatted_data = {
                "structured_data": material_info,
                "confidence_score": 0.95,  # High confidence for chatbot-generated content
                "extraction_type": "educational_content",
                "raw_response": "Generated by chatbot",
                "errors": []
            }
        else:
            # Already in OCR format
            ocr_formatted_data = material_info
        
        uploader = OCRClassroomUploader()
        result = uploader.upload_to_classroom(
            course_id=course_id,
            ocr_data=ocr_formatted_data,
            assignment_type="material"
        )
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error uploading material: {str(e)}"


@tool
def get_course_students(course_id: str) -> str:
    """Get all students enrolled in a specific Google Classroom course.
    
    Args:
        course_id: The ID of the course to get students for
        
    Returns:
        JSON string with student roster
    """
    try:
        import classroom_handler
        import json
        
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
        import json
        return json.dumps({
            "success": False,
            "error": f"Error getting course students: {str(e)}",
            "course_id": course_id
        }, indent=2)


class GoogleClassroomTool:
    """Google Classroom integration tools for LangGraph agent."""
    
    def get_tools(self):
        """Get all classroom tools."""
        return [get_courses, get_course_details, create_assignment, upload_material, get_course_students]