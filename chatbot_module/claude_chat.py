#!/usr/bin/env python3
"""
Claude-powered educational chatbot with LangGraph tools integration.
Uses Anthropic's Claude with actual Google Classroom access through LangGraph tools.
"""

import os
import sys
import json
import yaml
import time
from pathlib import Path
from typing import Optional, Dict, List, Any, Annotated, TypedDict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from langchain_anthropic import ChatAnthropic
    from langgraph.graph import StateGraph, START, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage
    from langgraph.graph.message import add_messages
    
    # Import classroom tools
    from chatbot_module.tools.classroom_tool import get_courses, get_course_details, create_assignment, upload_material
    
except ImportError as e:
    print(f"Warning: LangGraph dependencies not available: {e}")
    # Fallback to basic implementation
    ChatAnthropic = None


class State(TypedDict):
    """State for the LangGraph chatbot."""
    messages: Annotated[List[BaseMessage], add_messages]


class ClaudeChatbot:
    """Educational chatbot using Anthropic's Claude with LangGraph tools."""
    
    def __init__(self):
        self.api_key = self._get_claude_api_key()
        self.conversation_history = []
        self.tools = [get_courses, get_course_details, create_assignment, upload_material]
        self.model = None
        self.graph = None
        
        if ChatAnthropic is None:
            raise ImportError("LangGraph dependencies not available. Please install: pip install langchain-anthropic langgraph")
            
        self._initialize_model()
        self._build_graph()
    
    def _get_config(self) -> Optional[Dict]:
        """Load configuration from config.yml."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        except Exception:
            return None
    
    def _get_claude_api_key(self) -> Optional[str]:
        """Get Claude API key from config or environment."""
        config = self._get_config()
        
        # Try config file first
        if config and 'claude_api_chatbot_key' in config:
            return config['claude_api_chatbot_key']
        
        # Try environment variable
        return os.getenv('CLAUDE_API_KEY')
    
    def _initialize_model(self):
        """Initialize the Claude model with tools."""
        if not self.api_key:
            raise ValueError("No Claude API key found. Please set CLAUDE_API_KEY or add claude_api_chatbot_key to config.yml")
        
        # Initialize Claude model with tool binding
        self.model = ChatAnthropic(
            model="claude-3-haiku-20240307",
            api_key=self.api_key,
            temperature=0.3
        ).bind_tools(self.tools)
        
        print("✓ Claude model with LangGraph tools initialized")
    
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
        """Call the Claude model."""
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
        return """You are an educational AI assistant with direct access to Google Classroom data through specialized tools.

Your capabilities include:
1. **Google Classroom Access**: Use tools to get real course data, create assignments, and manage classroom content
2. **Educational Support**: Help with lesson planning, quiz creation, and teaching strategies  
3. **Course-Specific Guidance**: Provide personalized advice based on actual course information

Available Tools:
- get_courses(): Get all Google Classroom courses with details
- get_course_details(course_id): Get detailed information about a specific course
- create_assignment(course_id, title, description, type): Create assignments in Google Classroom
- upload_material(course_id, material_data): Upload educational materials to courses

IMPORTANT Instructions:
- When users ask about their courses, classes, or Google Classroom data, ALWAYS use the get_courses() tool first
- Use actual data from tools rather than making assumptions
- Be specific and helpful with course information
- Offer to help with course management tasks using the available tools

If users ask about their courses or classroom data, start by calling get_courses() to provide real information."""
    
    def send_message(self, message: str, user_id: str = "user") -> Dict[str, Any]:
        """Send a message to the chatbot and get a response."""
        try:
            # Record user message
            timestamp = time.time()
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": timestamp,
                "user_id": user_id
            }
            self.conversation_history.append(user_message)
            
            # Create messages for LangGraph
            messages = []
            
            # Add conversation history as context
            for msg in self.conversation_history[-10:]:  # Last 10 messages for context
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(SystemMessage(content=f"Previous response: {msg['content'][:200]}..."))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
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
    
    def get_model_type(self) -> str:
        """Return the model type identifier."""
        return "Claude Haiku + LangGraph Tools"
    
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
            file_path = f"conversation_export_claude_tools_{timestamp}.json"
        
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
    """Helper function with common educational prompts for Claude."""
    return {
        "my_courses": "What courses do I have in Google Classroom?",
        "course_details": "Show me details about my courses",
        "lesson_plan": "Help me create a lesson plan for one of my courses",
        "quiz_ideas": "Generate quiz questions for my course content",
        "create_assignment": "Help me create a new assignment in Google Classroom",
        "teaching_strategy": "What teaching strategies work best for my students?",
        "student_engagement": "How can I make my classes more engaging?",
        "upload_material": "Help me upload educational material to my course",
        "classroom_management": "What are some effective classroom management techniques?",
        "technology_integration": "How can I integrate technology effectively in my teaching?"
    }