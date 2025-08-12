#!/usr/bin/env python3
"""
LangGraph AI Agent for Google Classroom Student Management
This agent connects to Google Classroom and inserts new students from JSON files.
"""

import json
import os
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import yaml
import pickle
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AgentState(TypedDict):
    """State for the LangGraph agent"""
    students_data: List[Dict[str, Any]]
    processed_students: List[Dict[str, Any]]
    errors: List[str]
    current_step: str
    course_id: str


class GoogleClassroomAgent:
    """LangGraph-based AI agent for Google Classroom student management"""
    
    def __init__(self):
        self.service = None
        self.config = self._load_config()
        self.graph = self._build_graph()
    
    def _load_config(self):
        """Load configuration from config.yml"""
        try:
            with open("../config.yml", "r") as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config.yml: {e}")
            return None
    
    def _get_oauth_credentials(self, credentials_file):
        """Get OAuth credentials from file and token cache"""
        scopes = [
            'https://www.googleapis.com/auth/classroom.courses.readonly',
            'https://www.googleapis.com/auth/classroom.coursework.students',
            'https://www.googleapis.com/auth/classroom.rosters',
            'https://www.googleapis.com/auth/classroom.rosters.readonly'
        ]
        
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('../token.pickle'):
            with open('../token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, scopes)
                    creds = flow.run_local_server(port=0)
                else:
                    print(f"OAuth credentials file {credentials_file} not found.")
                    return None
            
            # Save the credentials for the next run
            with open('../token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
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
        """Connect to Google Classroom API"""
        print("Connecting to Google Classroom...")
        
        try:
            if not self.config:
                state["errors"].append("No configuration available")
                return state
            
            # First try service account from environment
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                scopes = [
                    'https://www.googleapis.com/auth/classroom.courses.readonly',
                    'https://www.googleapis.com/auth/classroom.coursework.students',
                    'https://www.googleapis.com/auth/classroom.rosters',
                    'https://www.googleapis.com/auth/classroom.rosters.readonly'
                ]
                creds = service_account.Credentials.from_service_account_file(
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=scopes
                )
                
                # Apply domain-wide delegation if teacher email is set
                subj = os.getenv("CLASSROOM_TEACHER_EMAIL")
                if subj:
                    creds = creds.with_subject(subj)
                
                self.service = build('classroom', 'v1', credentials=creds)
                state["current_step"] = "Connected to Google Classroom"
                print("Successfully connected to Google Classroom")
            
            # Try to use credentials file from config
            elif self.config.get('google_classroom_credentials_file'):
                credentials_file = os.path.join('..', self.config['google_classroom_credentials_file'])
                if os.path.exists(credentials_file):
                    scopes = [
                        'https://www.googleapis.com/auth/classroom.courses.readonly',
                        'https://www.googleapis.com/auth/classroom.coursework.students',
                        'https://www.googleapis.com/auth/classroom.rosters',
                        'https://www.googleapis.com/auth/classroom.rosters.readonly'
                    ]
                    
                    # Try as service account first
                    try:
                        creds = service_account.Credentials.from_service_account_file(
                            credentials_file, scopes=scopes
                        )
                        
                        # Apply domain-wide delegation if teacher email is set
                        subj = os.getenv("CLASSROOM_TEACHER_EMAIL")
                        if subj:
                            creds = creds.with_subject(subj)
                        
                        self.service = build('classroom', 'v1', credentials=creds)
                        state["current_step"] = "Connected to Google Classroom"
                        print("Successfully connected to Google Classroom using service account")
                    except Exception as sa_error:
                        print(f"Service account auth failed: {sa_error}")
                        print("Trying OAuth credentials...")
                        # Try OAuth flow
                        try:
                            creds = self._get_oauth_credentials(credentials_file)
                            if creds:
                                self.service = build('classroom', 'v1', credentials=creds)
                                state["current_step"] = "Connected to Google Classroom"
                                print("Successfully connected to Google Classroom using OAuth")
                            else:
                                self.service = "mock_service_with_api_key"
                                state["current_step"] = "Connected to Google Classroom (demo mode - OAuth flow failed)"
                                print("Connected in demo mode")
                        except Exception as oauth_error:
                            print(f"OAuth auth also failed: {oauth_error}")
                            self.service = "mock_service_with_api_key"
                            state["current_step"] = "Connected to Google Classroom (demo mode - all auth methods failed)"
                            print("Connected in demo mode")
                else:
                    print(f"Credentials file not found: {credentials_file}")
                    self.service = "mock_service_with_api_key"
                    state["current_step"] = "Connected to Google Classroom (demo mode - credentials file missing)"
                    print("Connected in demo mode")
            else:
                # For demo purposes, create a mock service with config API key
                print("No credentials configuration found.")
                print("Using demo mode with API key from config...")
                self.service = "mock_service_with_api_key"
                state["current_step"] = "Connected to Google Classroom (using API key - limited functionality)"
                print("Connected with API key (demo mode)")
                
        except Exception as e:
            state["errors"].append(f"Connection error: {str(e)}")
            print(f"Connection error: {str(e)}")
        
        return state
    
    def _load_students_from_json(self, state: AgentState) -> AgentState:
        """Load students data from JSON file"""
        print("Loading students from JSON file...")
        
        json_file_path = "../data/students.json"
        
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
        """Add students to Google Classroom"""
        print("Adding students to Google Classroom...")
        
        if not self.service:
            state["errors"].append("No classroom service available")
            return state
        
        added_count = 0
        
        for student in state["processed_students"]:
            try:
                if self.service == "mock_service_with_api_key":
                    # Demo mode - just simulate the invitation
                    print(f"DEMO MODE: Would invite student {student['first_name']} {student['last_name']} ({student['email']}) to course {student['course_id']}")
                    print(f"  Using API key from config: {self.config.get('google_classroom_api_key', 'Not found')[:20]}...")
                    added_count += 1
                else:
                    # Real mode - create actual invitation
                    invitation_body = {
                        'courseId': student['course_id'],
                        'userId': student['email'],
                        'role': 'STUDENT'
                    }
                    
                    # Send invitation
                    invitation = self.service.invitations().create(body=invitation_body).execute()
                    
                    print(f"Invited student: {student['first_name']} {student['last_name']} ({student['email']})")
                    added_count += 1
                
            except HttpError as error:
                error_msg = f"Failed to invite {student['email']}: {error}"
                state["errors"].append(error_msg)
                print(f"Failed to invite {student['email']}: {error}")
            except Exception as e:
                error_msg = f"Unexpected error for {student['email']}: {str(e)}"
                state["errors"].append(error_msg)
                print(f"Unexpected error for {student['email']}: {str(e)}")
        
        state["current_step"] = f"Successfully processed {added_count} students"
        print(f"Process completed! Processed {added_count} students total")
        
        return state
    
    def run(self, json_file_path: str = None) -> Dict[str, Any]:
        """Run the agent workflow"""
        print("Starting Google Classroom Student Management Agent...")
        
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
        print("AGENT EXECUTION SUMMARY")
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
    """Main function to run the agent"""
    # Create and run the agent
    agent = GoogleClassroomAgent()
    result = agent.run()
    
    # Save results to file
    output_file = "../data/agent_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()