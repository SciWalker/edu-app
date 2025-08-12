"""
Data extraction module using Gemini LLM with LangGraph for processing OCR text.
"""

import json
import time
import yaml
import logging
from typing import TypedDict, Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import os

import google.generativeai as genai
from langgraph.graph import StateGraph, END

import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.gemini_handler import MODEL_NAME, generate_node, build_graph


class ExtractionState(TypedDict):
    """State for the data extraction workflow."""
    raw_text: str
    extraction_type: str
    structured_data: Dict[str, Any]
    raw_response: str
    confidence_score: float
    errors: List[str]


class DataExtractor:
    """Handles data extraction from OCR text using Gemini LLM and LangGraph."""
    
    def __init__(self, config_path: str = "config.yml"):
        """
        Initialize data extractor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self._setup_gemini()
        self.graph = self._build_graph()
    
    def _setup_gemini(self):
        """Setup Gemini API configuration using existing handler."""
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)
            genai.configure(api_key=config["google_ai_studio_api_key"])
            self.model = genai.GenerativeModel(MODEL_NAME)
        except Exception as e:
            self.logger.error(f"Failed to setup Gemini: {str(e)}")
            raise
    
    def _create_extraction_prompt(self, text: str, extraction_type: str) -> str:
        """Create prompt for data extraction based on type."""
        base_prompt = f"""
        Extract structured information from the following OCR text. 
        Return ONLY valid JSON format.
        
        OCR Text:
        {text}
        
        """
        
        if extraction_type == "educational_content":
            return base_prompt + """
            Extract educational content with these keys:
            {
                "title": "string - main title or heading",
                "subject": "string - academic subject",
                "topics": ["list of key topics/concepts"],
                "questions": ["list of questions found"],
                "answers": ["list of answers if present"],
                "difficulty_level": "string - beginner/intermediate/advanced",
                "content_type": "string - worksheet/quiz/assignment/notes",
                "page_number": "string - if present"
            }
            """
        
        elif extraction_type == "form_data":
            return base_prompt + """
            Extract form data with these keys:
            {
                "form_type": "string - type of form",
                "fields": {
                    "field_name": "field_value"
                },
                "checkboxes": ["list of checked items"],
                "dates": ["list of dates found"],
                "signatures": ["list of signature fields"]
            }
            """
        
        elif extraction_type == "student_work":
            return base_prompt + """
            Extract student work information:
            {
                "student_name": "string - if present",
                "assignment_title": "string",
                "subject": "string",
                "responses": ["list of student answers"],
                "score": "string - if graded",
                "feedback": "string - teacher comments if present",
                "date": "string - if present"
            }
            """
        
        else:  # general extraction
            return base_prompt + """
            Extract any structured information you can identify:
            {
                "main_content": "string - primary content",
                "key_points": ["list of important points"],
                "entities": {
                    "names": ["person names"],
                    "dates": ["dates found"],
                    "numbers": ["important numbers"],
                    "locations": ["places mentioned"]
                },
                "document_type": "string - best guess of document type"
            }
            """
    
    def _extract_node(self, state: ExtractionState) -> ExtractionState:
        """Extract structured data using Gemini with existing handler patterns."""
        try:
            prompt = self._create_extraction_prompt(state["raw_text"], state["extraction_type"])
            
            time.sleep(1)  # Rate limiting (same as gemini_handler)
            response = self.model.generate_content(prompt)
            
            # Clean response text (remove markdown formatting if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Parse JSON response
            structured_data = json.loads(response_text)
            
            state["structured_data"] = structured_data
            state["raw_response"] = response.text  # Save original raw response
            state["confidence_score"] = self._calculate_confidence(structured_data)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Gemini response as JSON: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["structured_data"] = {}
            state["confidence_score"] = 0.0
            
        except Exception as e:
            error_msg = f"Data extraction failed: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["structured_data"] = {}
            state["confidence_score"] = 0.0
        
        return state
    
    def _validate_node(self, state: ExtractionState) -> ExtractionState:
        """Validate extracted data quality."""
        structured_data = state["structured_data"]
        
        if not structured_data:
            state["errors"].append("No structured data extracted")
            return state
        
        # Basic validation checks
        validation_errors = []
        
        # Check for empty values
        empty_fields = [k for k, v in structured_data.items() if not v]
        if empty_fields:
            validation_errors.append(f"Empty fields: {empty_fields}")
        
        # Update confidence based on validation
        if validation_errors:
            state["confidence_score"] *= 0.7
            state["errors"].extend(validation_errors)
        
        return state
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted data."""
        if not data:
            return 0.0
        
        # Simple heuristic based on data completeness
        filled_fields = sum(1 for v in data.values() if v)
        total_fields = len(data)
        
        base_confidence = filled_fields / total_fields if total_fields > 0 else 0.0
        
        # Boost confidence if we have rich structured data
        if isinstance(data, dict) and len(data) > 3:
            base_confidence = min(1.0, base_confidence * 1.2)
        
        return round(base_confidence, 2)
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph for data extraction workflow using existing handler patterns."""
        graph = StateGraph(ExtractionState)
        
        # Add nodes
        graph.add_node("extract", self._extract_node)
        graph.add_node("validate", self._validate_node)
        
        # Define edges (same pattern as gemini_handler)
        graph.add_edge("extract", "validate")
        graph.add_edge("validate", END)
        
        # Set entry point
        graph.set_entry_point("extract")
        
        return graph.compile()
    
    def _save_result(self, result: Dict[str, Any], extraction_type: str):
        """Save extraction result to processed_data folder."""
        try:
            # Create processed_data directory if it doesn't exist
            processed_dir = Path("processed_data")
            processed_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{extraction_type}_{timestamp}.json"
            filepath = processed_dir / filename
            
            # Save result to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Results saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
    
    def extract_data(
        self, 
        text: str, 
        extraction_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract structured data from text.
        
        Args:
            text: OCR text to process
            extraction_type: Type of extraction (educational_content, form_data, student_work, general)
            
        Returns:
            Dictionary containing extracted structured data
        """
        initial_state = ExtractionState(
            raw_text=text,
            extraction_type=extraction_type,
            structured_data={},
            raw_response="",
            confidence_score=0.0,
            errors=[]
        )
        
        try:
            result = self.graph.invoke(initial_state)
            
            # Save results to processed_data folder
            processed_result = {
                "structured_data": result["structured_data"],
                "raw_response": result["raw_response"],
                "confidence_score": result["confidence_score"],
                "extraction_type": result["extraction_type"],
                "errors": result["errors"],
                "raw_text_length": len(text),
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_result(processed_result, extraction_type)
            
            return processed_result
        except Exception as e:
            self.logger.error(f"Graph execution failed: {str(e)}")
            return {
                "structured_data": {},
                "raw_response": "",
                "confidence_score": 0.0,
                "extraction_type": extraction_type,
                "errors": [str(e)],
                "raw_text_length": len(text)
            }