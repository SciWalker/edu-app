"""
Data extraction module using LLM with LangGraph for processing OCR text.
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

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

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
    """Handles data extraction from OCR text using multiple LLM providers and LangGraph."""
    
    def __init__(self, config_path: str = "config.yml", provider: str = "gemini"):
        """
        Initialize data extractor.
        
        Args:
            config_path: Path to configuration file
            provider: AI provider to use ('gemini' or 'claude')
        """
        self.config_path = config_path
        self.provider = provider.lower()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup the selected provider
        if self.provider == "claude":
            self._setup_claude()
        else:
            self._setup_gemini()
            
        self.graph = self._build_graph()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            # Try multiple possible locations for config.yml
            config_paths = [
                self.config_path,
                os.path.join(os.path.dirname(__file__), '..', self.config_path),
                os.path.join(os.getcwd(), self.config_path)
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, "r") as file:
                        config = yaml.safe_load(file)
                        self.logger.info(f"Config loaded from: {path}")
                        return config
            
            raise FileNotFoundError(f"config.yml not found in any of: {config_paths}")
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            return {}
    
    def _setup_claude(self):
        """Setup Claude API configuration."""
        if not CLAUDE_AVAILABLE:
            raise ImportError("anthropic package not available. Install with: pip install anthropic")
            
        try:
            # Try to get Claude API key from config or environment
            claude_api_key = (
                self.config.get("claude_api_chatbot_key") or 
                os.getenv("CLAUDE_API_KEY") or
                os.getenv("ANTHROPIC_API_KEY")
            )
            
            if not claude_api_key:
                raise ValueError("Claude API key not found in config.yml or environment variables")
            
            self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
            self.logger.info("Claude API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Claude: {str(e)}")
            raise
    
    def _setup_gemini(self):
        """Setup Gemini API configuration using existing handler."""
        try:
            api_key = self.config.get("google_ai_studio_api_key")
            if not api_key:
                raise ValueError("google_ai_studio_api_key not found in config.yml")
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)
            self.logger.info("Gemini API client initialized successfully")
            
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
            Create a comprehensive lesson plan from this content. Return JSON with these keys:
            {
                "title": "string - lesson title",
                "subject": "string - academic subject",
                "grade_level": "string - target grade/age group",
                "duration": "string - estimated lesson time (e.g., '50 minutes', '2 hours')",
                "learning_objectives": ["specific learning goals students will achieve"],
                "key_topics": ["main topics and concepts covered"],
                "lesson_structure": {
                    "introduction": "string - lesson opening activity (5-10 min)",
                    "main_activities": ["detailed list of core learning activities with time estimates"],
                    "assessment": "string - how to evaluate student understanding",
                    "conclusion": "string - lesson wrap-up and summary"
                },
                "materials_needed": ["textbooks, worksheets, technology, etc."],
                "vocabulary": ["key terms students should learn"],
                "homework_assignments": ["suggested follow-up work"],
                "differentiation": "string - how to adapt for different learning needs",
                "extension_activities": ["optional advanced activities for fast learners"],
                "assessment_criteria": ["how students will be evaluated"],
                "difficulty_level": "string - beginner/intermediate/advanced",
                "prerequisite_knowledge": ["what students should know before this lesson"],
                "cross_curricular_links": ["connections to other subjects"]
            }
            
            Make the lesson plan detailed, practical, and classroom-ready.
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
        
        elif extraction_type == "quiz":
            return base_prompt + """
            Extract educational content optimized for quiz generation:
            {
                "title": "string - main title or topic",
                "subject": "string - academic subject",
                "key_concepts": ["list of main concepts and topics"],
                "important_facts": ["list of factual information suitable for questions"],
                "definitions": ["list of key terms and their definitions"],
                "examples": ["list of examples mentioned"],
                "formulas": ["list of formulas or equations if present"],
                "processes": ["list of step-by-step processes"],
                "difficulty_level": "string - beginner/intermediate/advanced",
                "question_types": ["suggested question types: multiple_choice, true_false, short_answer"]
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
        """Extract structured data using the selected AI provider."""
        if self.provider == "claude":
            return self._extract_with_claude(state)
        else:
            return self._extract_with_gemini(state)
    
    def _extract_with_claude(self, state: ExtractionState) -> ExtractionState:
        """Extract structured data using Claude API."""
        try:
            prompt = self._create_extraction_prompt(state["raw_text"], state["extraction_type"])
            
            time.sleep(1)  # Rate limiting
            
            # Use Claude 3 Haiku with streaming for large requests
            response_text = ""
            with self.claude_client.messages.stream(
                model="claude-3-haiku-20240307",  # Working Haiku model
                max_tokens=4096,  # Haiku's maximum output tokens
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    response_text += text
            
            # Clean response text (remove markdown formatting if present)
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Parse JSON response
            structured_data = json.loads(response_text)
            
            state["structured_data"] = structured_data
            state["raw_response"] = response_text  # Save streamed response
            state["confidence_score"] = self._calculate_confidence(structured_data)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Claude response as JSON: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            state["structured_data"] = {}
            state["confidence_score"] = 0.0
            
        except Exception as e:
            error_msg = f"Claude data extraction failed: {str(e)}"
            self.logger.error(f"Claude API error details: {type(e).__name__}: {str(e)}")
            
            # Provide more specific error messages
            if "connection" in str(e).lower():
                error_msg = f"Failed to connect to Claude API. Check network connection and API endpoint."
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                error_msg = f"Claude API authentication failed. Check your API key in config.yml."
            elif "rate" in str(e).lower() or "quota" in str(e).lower():
                error_msg = f"Claude API rate limit or quota exceeded. Try again later."
            
            state["errors"].append(error_msg)
            state["structured_data"] = {}
            state["confidence_score"] = 0.0
        
        return state

    def _extract_with_gemini(self, state: ExtractionState) -> ExtractionState:
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
            error_msg = f"Gemini data extraction failed: {str(e)}"
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