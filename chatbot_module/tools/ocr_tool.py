#!/usr/bin/env python3
"""
OCR processing tools for LangGraph educational agent.
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
def process_image(image_path: str, extraction_type: str = "educational_content") -> str:
    """Process an image using OCR to extract educational content.
    
    Args:
        image_path: Path to the image file to process
        extraction_type: Type of content to extract (educational_content, quiz, general)
        
    Returns:
        JSON string with extracted content and metadata
    """
    try:
        from ocr_module import OCRPipeline
        import json
        
        # Initialize OCR pipeline
        pipeline = OCRPipeline()
        
        # Process the image
        result = pipeline.process_image(
            image_path=image_path,
            extraction_type=extraction_type,
            preprocess=True
        )
        
        if result.get('pipeline_status') == 'success':
            return json.dumps({
                "success": True,
                "extracted_text": result.get('ocr_result', {}).get('text', ''),
                "structured_data": result.get('extracted_data', {}).get('structured_data', {}),
                "confidence_score": result.get('extracted_data', {}).get('confidence_score', 0),
                "extraction_type": extraction_type,
                "message": "Image processed successfully"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Unknown OCR error'),
                "message": "Failed to process image"
            }, indent=2)
            
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "OCR processing failed"
        }, indent=2)


@tool
def extract_quiz_from_image(image_path: str) -> str:
    """Extract quiz questions from an image and generate structured quiz data.
    
    Args:
        image_path: Path to the image file containing quiz content
        
    Returns:
        JSON string with generated quiz questions and answers
    """
    try:
        from ocr_module import OCRPipeline
        import json
        
        # Initialize OCR pipeline
        pipeline = OCRPipeline()
        
        # Process image with quiz extraction
        result = pipeline.process_image(
            image_path=image_path,
            extraction_type="quiz",
            preprocess=True
        )
        
        if result.get('pipeline_status') == 'success':
            # Generate quiz from the extracted content
            from src.generate_quiz import generate_quiz_with_gemini
            
            ocr_text = result.get('ocr_result', {}).get('text', '')
            lesson_plan = {
                'topic': result.get('extracted_data', {}).get('structured_data', {}).get('subject', 'General Knowledge'),
                'content': ocr_text,
                'number_of_questions': 5,
                'response_type': 'multiple_choice_question'
            }
            
            quiz_data = generate_quiz_with_gemini(lesson_plan)
            
            return json.dumps({
                "success": True,
                "quiz_data": quiz_data,
                "source_text": ocr_text,
                "confidence_score": result.get('extracted_data', {}).get('confidence_score', 0),
                "message": "Quiz generated successfully from image"
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Failed to extract content from image'),
                "message": "Could not generate quiz from image"
            }, indent=2)
            
    except Exception as e:
        import json
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Quiz generation from image failed"
        }, indent=2)