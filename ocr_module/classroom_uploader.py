"""
OCR to Google Classroom uploader module.
Converts OCR extracted educational content to Google Classroom materials.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Add src to path to import classroom_handler
sys.path.append(str(Path(__file__).parent.parent / "src"))
from classroom_handler import create_quiz_assignment, get_classroom_service, list_courses


class OCRClassroomUploader:
    """Handles uploading OCR extracted content to Google Classroom."""
    
    def __init__(self):
        """Initialize the uploader."""
        self.service = get_classroom_service()
    
    def convert_ocr_to_assignment(
        self, 
        ocr_data: Dict[str, Any], 
        assignment_type: str = "material"
    ) -> Dict[str, Any]:
        """
        Convert OCR extracted data to Google Classroom assignment format.
        
        Args:
            ocr_data: OCR extraction result from data_extractor
            assignment_type: Type of assignment (material, quiz, assignment)
            
        Returns:
            Dictionary in Google Classroom format
        """
        structured_data = ocr_data.get('structured_data', {})
        
        if assignment_type == "material":
            return self._create_material_format(structured_data)
        elif assignment_type == "quiz" and structured_data.get('questions'):
            return self._create_quiz_format(structured_data)
        else:
            return self._create_assignment_format(structured_data)
    
    def _create_material_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create material format for Google Classroom."""
        title = data.get('title', 'Educational Material')
        subject = data.get('subject', 'General')
        topics = data.get('topics', [])
        
        # Build description from topics
        description = f"**Subject:** {subject}\n\n"
        
        if topics:
            description += "**Key Topics:**\n"
            for i, topic in enumerate(topics, 1):
                description += f"{i}. {topic}\n"
            description += "\n"
        
        content_type = data.get('content_type', 'Notes')
        difficulty = data.get('difficulty_level', 'Not specified')
        
        description += f"**Content Type:** {content_type}\n"
        description += f"**Difficulty Level:** {difficulty}\n"
        
        return {
            'title': f"{title} - {subject}",
            'description': description,
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
            'maxPoints': 0  # Material assignment, no points
        }
    
    def _create_quiz_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create quiz format for Google Classroom."""
        title = data.get('title', 'Quiz')
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        
        # Build quiz description
        description = f"**Quiz: {title}**\n\n"
        
        for i, question in enumerate(questions, 1):
            description += f"**Question {i}:** {question}\n"
            if i <= len(answers) and answers[i-1]:
                description += f"**Answer:** {answers[i-1]}\n"
            description += "\n"
        
        return {
            'title': f"Quiz: {title}",
            'description': description,
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
            'maxPoints': len(questions) * 10  # 10 points per question
        }
    
    def _create_assignment_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create general assignment format for Google Classroom."""
        title = data.get('title', 'Assignment')
        subject = data.get('subject', 'General')
        topics = data.get('topics', [])
        
        description = f"**Assignment: {title}**\n\n"
        description += f"**Subject:** {subject}\n\n"
        
        if topics:
            description += "**Topics to Cover:**\n"
            for topic in topics:
                description += f"• {topic}\n"
        
        return {
            'title': f"{title} - {subject}",
            'description': description,
            'workType': 'ASSIGNMENT', 
            'state': 'PUBLISHED',
            'maxPoints': 100
        }
    
    def upload_to_classroom(
        self, 
        course_id: str,
        ocr_data: Dict[str, Any],
        assignment_type: str = "material",
        due_date_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Upload OCR extracted content to Google Classroom.
        
        Args:
            course_id: Google Classroom course ID
            ocr_data: OCR extraction result
            assignment_type: Type of assignment (material, quiz, assignment)
            due_date_days: Days from now for due date (optional)
            
        Returns:
            Result dictionary with success status and details
        """
        if not self.service:
            return {
                "success": False,
                "error": "Could not connect to Google Classroom service"
            }
        
        try:
            # Convert OCR data to classroom format
            assignment_data = self.convert_ocr_to_assignment(ocr_data, assignment_type)
            
            # Add due date if specified
            if due_date_days:
                due_date = datetime.now() + timedelta(days=due_date_days)
                assignment_data['dueDate'] = {
                    'year': due_date.year,
                    'month': due_date.month,
                    'day': due_date.day
                }
            
            # Create the assignment in Google Classroom
            assignment = self.service.courses().courseWork().create(
                courseId=course_id,
                body=assignment_data
            ).execute()
            
            return {
                "success": True,
                "assignment_id": assignment.get('id'),
                "course_id": course_id,
                "title": assignment.get('title'),
                "state": assignment.get('state'),
                "max_points": assignment.get('maxPoints'),
                "alternate_link": assignment.get('alternateLink'),
                "assignment_type": assignment_type,
                "message": f"Successfully uploaded {assignment_type} '{assignment.get('title')}' to course {course_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to upload to classroom: {str(e)}",
                "course_id": course_id
            }
    
    def upload_from_file(
        self,
        course_id: str, 
        processed_file_path: str,
        assignment_type: str = "material",
        due_date_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load processed OCR data from file and upload to Google Classroom.
        
        Args:
            course_id: Google Classroom course ID
            processed_file_path: Path to processed OCR JSON file
            assignment_type: Type of assignment (material, quiz, assignment)
            due_date_days: Days from now for due date (optional)
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Load processed OCR data
            with open(processed_file_path, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)
            
            # Upload to classroom
            result = self.upload_to_classroom(
                course_id=course_id,
                ocr_data=ocr_data,
                assignment_type=assignment_type,
                due_date_days=due_date_days
            )
            
            result['source_file'] = processed_file_path
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load file {processed_file_path}: {str(e)}"
            }
    
    def get_available_courses(self) -> List[Dict[str, Any]]:
        """Get list of available Google Classroom courses."""
        return list_courses()