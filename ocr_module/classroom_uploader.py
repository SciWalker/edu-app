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
        """Create comprehensive lesson plan format for Google Classroom."""
        title = data.get('title', 'Lesson Plan')
        subject = data.get('subject', 'General')
        grade_level = data.get('grade_level', 'Not specified')
        duration = data.get('duration', 'Not specified')
        
        # Build comprehensive lesson plan description
        description = f"# {title}\n\n"
        description += f"**Subject:** {subject} | **Grade Level:** {grade_level} | **Duration:** {duration}\n"
        description += f"**Difficulty:** {data.get('difficulty_level', 'Not specified')}\n\n"
        
        # Learning Objectives
        objectives = data.get('learning_objectives', [])
        if objectives:
            description += "## 🎯 Learning Objectives\n"
            for obj in objectives:
                description += f"• {obj}\n"
            description += "\n"
        
        # Key Topics
        key_topics = data.get('key_topics', [])
        if key_topics:
            description += "## 📚 Key Topics\n"
            for topic in key_topics:
                description += f"• {topic}\n"
            description += "\n"
        
        # Lesson Structure
        lesson_structure = data.get('lesson_structure', {})
        if lesson_structure:
            description += "## 🏗️ Lesson Structure\n\n"
            
            if lesson_structure.get('introduction'):
                description += f"**Introduction:** {lesson_structure['introduction']}\n\n"
            
            main_activities = lesson_structure.get('main_activities', [])
            if main_activities:
                description += "**Main Activities:**\n"
                for i, activity in enumerate(main_activities, 1):
                    description += f"{i}. {activity}\n"
                description += "\n"
            
            if lesson_structure.get('assessment'):
                description += f"**Assessment:** {lesson_structure['assessment']}\n\n"
            
            if lesson_structure.get('conclusion'):
                description += f"**Conclusion:** {lesson_structure['conclusion']}\n\n"
        
        # Materials Needed
        materials = data.get('materials_needed', [])
        if materials:
            description += "## 📦 Materials Needed\n"
            for material in materials:
                description += f"• {material}\n"
            description += "\n"
        
        # Vocabulary
        vocabulary = data.get('vocabulary', [])
        if vocabulary:
            description += "## 📖 Key Vocabulary\n"
            description += f"{', '.join(vocabulary)}\n\n"
        
        # Assessment Criteria
        assessment_criteria = data.get('assessment_criteria', [])
        if assessment_criteria:
            description += "## ✅ Assessment Criteria\n"
            for criteria in assessment_criteria:
                description += f"• {criteria}\n"
            description += "\n"
        
        # Homework Assignments
        homework = data.get('homework_assignments', [])
        if homework:
            description += "## 📝 Homework Assignments\n"
            for hw in homework:
                description += f"• {hw}\n"
            description += "\n"
        
        # Extension Activities
        extensions = data.get('extension_activities', [])
        if extensions:
            description += "## 🚀 Extension Activities\n"
            for ext in extensions:
                description += f"• {ext}\n"
            description += "\n"
        
        # Differentiation
        differentiation = data.get('differentiation')
        if differentiation:
            description += "## 🔄 Differentiation\n"
            description += f"{differentiation}\n\n"
        
        # Prerequisite Knowledge
        prerequisites = data.get('prerequisite_knowledge', [])
        if prerequisites:
            description += "## 📋 Prerequisite Knowledge\n"
            for prereq in prerequisites:
                description += f"• {prereq}\n"
            description += "\n"
        
        return {
            'title': f"{title} - {subject}",
            'description': description.strip(),
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