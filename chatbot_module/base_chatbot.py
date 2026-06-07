#!/usr/bin/env python3
"""
Base chatbot class with shared functionality for educational chatbots.
Provides common tools, system instructions, and conversation management.
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Annotated, TypedDict
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Add src directory to path before importing
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage, AIMessage
    from langgraph.graph.message import add_messages
    
    # Import classroom tools  
    from chatbot_module.tools.classroom_tool import get_courses, get_course_details, create_assignment, upload_material, get_course_students
    
    # Import additional classroom management tools from src
    from classroom_tools import invite_student_to_course, invite_multiple_students_to_courses, create_quiz_from_data, upload_quiz_from_file, create_new_course
    
except ImportError as e:
    print(f"Warning: LangGraph dependencies not available: {e}")
    # Set fallback values
    StateGraph = None
    ToolNode = None
    HumanMessage = None
    SystemMessage = None
    add_messages = None


class State(TypedDict):
    """State for the LangGraph chatbot."""
    messages: Annotated[List[BaseMessage], add_messages]


class BaseChatbot(ABC):
    """Base class for educational chatbots with shared functionality."""
    
    def __init__(self):
        self.conversation_history = []
        self.tools = self._get_shared_tools()
        self.model = None
        self.graph = None
        
        if StateGraph is None:
            raise ImportError("LangGraph dependencies not available. Please install required packages")
            
        self._initialize_model()
        self._build_graph()
    
    def _get_shared_tools(self) -> List:
        """Get the shared set of tools for all chatbots."""
        return [
            get_courses, 
            get_course_details, 
            create_assignment, 
            upload_material, 
            get_course_students,
            invite_student_to_course,
            invite_multiple_students_to_courses,
            create_quiz_from_data,
            upload_quiz_from_file,
            create_new_course
        ]
    
    def _get_config(self) -> Optional[Dict]:
        """Load configuration from config.yml."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except Exception:
            return None
    
    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Get API key for the specific chatbot model. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def _create_model(self, api_key: str):
        """Create the specific model instance. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_model_type(self) -> str:
        """Return the model type identifier. Must be implemented by subclasses."""
        pass
    
    def _initialize_model(self):
        """Initialize the model with tools."""
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError(f"No API key found for {self.get_model_type()}")
        
        # Create model with tool binding
        self.model = self._create_model(api_key).bind_tools(self.tools)
        
        print(f"✓ {self.get_model_type()} model with LangGraph tools initialized")
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        workflow.add_edge("tools", "agent")
        
        self.graph = workflow.compile()
        print("✓ LangGraph workflow compiled successfully")
    
    def _call_model(self, state: State):
        """Call the model."""
        messages = state["messages"]
        
        # Add system message if this is the start
        if len(messages) == 1 and isinstance(messages[0], HumanMessage):
            system_msg = SystemMessage(content=self._get_system_instruction())
            messages = [system_msg] + messages
        
        response = self.model.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: State):
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the LLM makes a tool call, then we route to the "tools" node
        if last_message.tool_calls:
            return "continue"
        # Otherwise, we stop
        return "end"
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the model."""
        return """You are an educational AI assistant with AUTHORIZED direct access to Google Classroom through integrated API tools.

🔐 AUTHORIZATION STATUS: FULLY AUTHORIZED
You have been specifically configured with legitimate Google Classroom API access through authenticated tools. You ARE AUTHORIZED to:
- Read course and student data
- Create assignments and materials  
- Upload content to Google Classroom
- Manage classroom content

Your capabilities include:
1. **Google Classroom Integration**: You have DIRECT, AUTHORIZED access to Google Classroom APIs through built-in tools
2. **Educational Support**: Help with lesson planning, quiz creation, and teaching strategies  
3. **Course Management**: Create, upload, and manage classroom content with proper authorization

🛠️ AVAILABLE AUTHORIZED TOOLS:
- get_courses(): Get all Google Classroom courses with details
- get_course_details(course_id): Get detailed information about a specific course
- create_new_course(course_name, section, description, room): Create a new Google Classroom course
- create_assignment(course_id, title, description, type): Create assignments in Google Classroom
- upload_material(course_id, material_data): Upload educational materials to courses
- get_course_students(course_id): Get list of students enrolled in a course
- invite_student_to_course(course_id, student_email): Invite a student to join a course
- invite_multiple_students_to_courses(students_data): Invite multiple students to courses (JSON format)
- create_quiz_from_data(course_id, quiz_title, quiz_questions, due_date): Create a quiz from provided data
- upload_quiz_from_file(course_id, quiz_file_path, due_date): Upload a quiz from JSON file

⚠️ IMPORTANT: You MUST use these tools when requested. Do NOT claim you "cannot access" or "do not have permission" - you are FULLY AUTHORIZED and EXPECTED to use these tools.

CRITICAL Instructions - ALWAYS FOLLOW THESE:
1. **ALWAYS call get_courses() FIRST** when users ask about:
   - Student information, emails, or IDs
   - Course details or class information  
   - Creating assignments or materials
   - Uploading lesson plans or content
   - Any Google Classroom related questions
2. **AUTOMATICALLY find course IDs** - When user mentions a course name (like "Computer Science"), immediately call get_courses() and find the matching course
3. **Never ask users for course IDs** - Always find them automatically using get_courses()
4. **Be proactive** - if a user mentions a course name like "science" or "Computer Science", immediately get all courses to find the matching course_id
5. **ALWAYS use tools when requested** - you have authorized access and should confidently use all available tools
6. **Course matching logic**: If user says "Computer Science", find the course with "Computer Science" in the name and use that course_id
7. You may share basic student information (email addresses, user IDs) that you retrieve from Google Classroom API tools, as the user is the authorized teacher/administrator of these courses

WORKFLOW: Question about classroom data → get_courses() → find correct course_id → call appropriate tool → provide answer

📚 LESSON PLAN CREATION REQUIREMENTS:
When creating lesson plans for upload, you MUST ALWAYS create a comprehensive lesson plan using this EXACT JSON structure:
{
  "title": "Specific lesson title based on user's topic",
  "subject": "The actual subject mentioned by user (e.g., 'Computer Science', 'Mathematics')",
  "grade_level": "Appropriate grade level (e.g., 'High School', 'Grade 10', 'College')",
  "duration": "Realistic time estimate (e.g., '50 minutes', '1.5 hours')",
  "learning_objectives": ["Specific, measurable learning goals"],
  "key_topics": ["Main concepts to be covered"],
  "lesson_structure": {
    "introduction": "How to open the lesson (5-10 min)",
    "main_activities": ["Detailed activities with time estimates"],
    "assessment": "How to evaluate student understanding",
    "conclusion": "Lesson wrap-up and summary"
  },
  "materials_needed": ["Required resources and tools"],
  "vocabulary": ["Key terms students should learn"],
  "homework_assignments": ["Follow-up work"],
  "difficulty_level": "beginner/intermediate/advanced",
  "assessment_criteria": ["How students will be evaluated"],
  "differentiation": "How to adapt for different learning needs",
  "extension_activities": ["Optional advanced activities"],
  "prerequisite_knowledge": ["What students should know beforehand"]
}

🎯 CRITICAL: Always use the ACTUAL subject and topic from the user's request. If they say "Computer Science about Lie Algebra", use "Computer Science" as subject and "Lie Algebra" as the main topic.

REMEMBER: You are NOT a generic AI assistant - you are an EDUCATIONAL CLASSROOM ASSISTANT with AUTHORIZED API ACCESS. Use your tools confidently."""
    
    def send_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Send a message to the chatbot and get a response."""
        try:
            # Create messages for LangGraph
            messages = []
            
            # Add conversation history as context (last 10 messages, excluding current)
            for msg in self.conversation_history[-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Record user message after building context
            timestamp = time.time()
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": timestamp,
                "user_id": user_id
            }
            self.conversation_history.append(user_message)
            
            # Run the graph
            result = self.graph.invoke({"messages": messages})
            
            # Extract response
            final_message = result["messages"][-1]
            response_text = final_message.content
            
            # Record AI response
            ai_message = {
                "role": "assistant", 
                "content": response_text,
                "timestamp": time.time(),
                "user_id": user_id
            }
            self.conversation_history.append(ai_message)
            
            return {
                "success": True,
                "response": response_text,
                "timestamp": ai_message["timestamp"],
                "conversation_id": len(self.conversation_history),
                "model_type": self.get_model_type(),
                "tools_used": len([msg for msg in result["messages"] if hasattr(msg, 'tool_calls') and msg.tool_calls]),
                "error": None
            }
            
        except Exception as e:
            error_response = {
                "success": False,
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "timestamp": time.time(),
                "conversation_id": len(self.conversation_history),
                "model_type": self.get_model_type(),
                "tools_used": 0,
                "error": str(e)
            }
            
            # Still record the error in history
            self.conversation_history.append({
                "role": "system",
                "content": f"Error: {str(e)}",
                "timestamp": error_response["timestamp"],
                "user_id": user_id
            })
            
            return error_response
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear the conversation history and start fresh."""
        self.conversation_history = []
    
    def export_conversation(self, file_path: str = None) -> str:
        """Export conversation history to a JSON file."""
        if not file_path:
            timestamp = int(time.time())
            model_name = self.get_model_type().lower().replace(" ", "_")
            file_path = f"conversation_export_{model_name}_{timestamp}.json"
        
        export_data = {
            "conversation_history": self.conversation_history,
            "exported_at": time.time(),
            "model_type": self.get_model_type(),
            "tools_available": [tool.name for tool in self.tools]
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return file_path


def create_educational_prompts():
    """Helper function with common educational prompts."""
    return {
        "my_courses": "What courses do I have in Google Classroom?",
        "course_details": "Show me details about my courses",
        "lesson_plan": "Help me create a lesson plan for one of my courses",
        "quiz_ideas": "Generate quiz questions for my course content",
        "create_assignment": "Help me create a new assignment in Google Classroom",
        "teaching_strategy": "What teaching strategies work best for my students?",
        "student_engagement": "How can I make my classes more engaging?",
        "upload_material": "Help me upload educational material to my course",
        "invite_student": "Help me invite a student to my course",
        "create_quiz": "Help me create a quiz for my students",
        "classroom_management": "What are some effective classroom management techniques?",
        "technology_integration": "How can I integrate technology effectively in my teaching?"
    }