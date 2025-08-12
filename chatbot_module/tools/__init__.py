"""
Tools module for LangGraph educational agent.
"""

from .classroom_tool import get_courses, get_course_details, create_assignment, upload_material
from .ocr_tool import process_image, extract_quiz_from_image
from .quiz_tool import generate_quiz, create_classroom_quiz, generate_lesson_quiz

__all__ = [
    'get_courses', 'get_course_details', 'create_assignment', 'upload_material',
    'process_image', 'extract_quiz_from_image', 
    'generate_quiz', 'create_classroom_quiz', 'generate_lesson_quiz'
]