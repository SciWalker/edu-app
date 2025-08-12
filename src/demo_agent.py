#!/usr/bin/env python3
"""
Demo version of the LangGraph Google Classroom Agent
This shows how the agent works without requiring actual Google Classroom credentials
"""

import json
import os
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    students_data: List[Dict[str, Any]]
    processed_students: List[Dict[str, Any]]
    errors: List[str]
    current_step: str
    course_id: str


class DemoGoogleClassroomAgent:
    """Demo LangGraph-based AI agent for Google Classroom student management"""
    
    def __init__(self):
        self.service = "mock_service"  # Mock service for demo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("connect_classroom", self._connect_to_classroom)
        workflow.add_node("load_students", self._load_students_from_json)
        workflow.add_node("process_students", self._process_students)
        workflow.add_node("add_students", self._add_students_to_classroom)
        
        # Add edges
        workflow.add_edge(START, "connect_classroom")
        workflow.add_edge("connect_classroom", "load_students")
        workflow.add_edge("load_students", "process_students")
        workflow.add_edge("process_students", "add_students")
        workflow.add_edge("add_students", END)
        
        return workflow.compile()
    
    def _connect_to_classroom(self, state: AgentState) -> AgentState:
        """Mock connection to Google Classroom API"""
        print("Connecting to Google Classroom...")
        
        # Simulate successful connection
        state["current_step"] = "Connected to Google Classroom (DEMO MODE)"
        print("Successfully connected to Google Classroom (DEMO MODE)")
        
        return state
    
    def _load_students_from_json(self, state: AgentState) -> AgentState:
        """Load students data from JSON file"""
        print("Loading students from JSON file...")
        
        json_file_path = "data/students.json"
        
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    state["students_data"] = data.get("students", [])
                    state["current_step"] = f"Loaded {len(state['students_data'])} students from JSON"
                    print(f"Loaded {len(state['students_data'])} students from {json_file_path}")
            else:
                state["errors"].append(f"JSON file not found: {json_file_path}")
                print(f"JSON file not found: {json_file_path}")
        except Exception as e:
            state["errors"].append(f"Error loading JSON: {str(e)}")
            print(f"Error loading JSON: {str(e)}")
        
        return state
    
    def _process_students(self, state: AgentState) -> AgentState:
        """Process and validate student data"""
        print("Processing student data...")
        
        processed = []
        
        for student in state["students_data"]:
            if self._validate_student_data(student):
                processed.append(student)
                print(f"Validated student: {student['first_name']} {student['last_name']}")
            else:
                state["errors"].append(f"Invalid student data: {student}")
                print(f"Invalid student data: {student}")
        
        state["processed_students"] = processed
        state["current_step"] = f"Processed {len(processed)} valid students"
        
        return state
    
    def _validate_student_data(self, student: Dict[str, Any]) -> bool:
        """Validate student data structure"""
        required_fields = ["first_name", "last_name", "email", "course_id"]
        return all(field in student and student[field] for field in required_fields)
    
    def _add_students_to_classroom(self, state: AgentState) -> AgentState:
        """Mock adding students to Google Classroom"""
        print("Adding students to Google Classroom (DEMO MODE)...")
        
        added_count = 0
        
        for student in state["processed_students"]:
            # Simulate successful invitation
            print(f"DEMO: Would invite student: {student['first_name']} {student['last_name']} ({student['email']}) to course {student['course_id']}")
            added_count += 1
        
        state["current_step"] = f"Successfully processed {added_count} students (DEMO MODE)"
        print(f"Process completed! Would have invited {added_count} students total")
        
        return state
    
    def run(self) -> Dict[str, Any]:
        """Run the agent workflow"""
        print("Starting Google Classroom Student Management Agent (DEMO MODE)...")
        
        # Initialize state
        initial_state = {
            "students_data": [],
            "processed_students": [],
            "errors": [],
            "current_step": "Starting agent",
            "course_id": ""
        }
        
        # Run the workflow
        result = self.graph.invoke(initial_state)
        
        # Print summary
        print("\n" + "="*50)
        print("AGENT EXECUTION SUMMARY (DEMO)")
        print("="*50)
        print(f"Final Step: {result['current_step']}")
        print(f"Students Processed: {len(result['processed_students'])}")
        print(f"Errors: {len(result['errors'])}")
        
        if result['errors']:
            print("\nErrors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        return result


def main():
    """Main function to run the demo agent"""
    # Create and run the demo agent
    agent = DemoGoogleClassroomAgent()
    result = agent.run()
    
    # Save results to file
    output_file = "data/demo_agent_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nDemo results saved to {output_file}")


if __name__ == "__main__":
    main()