#!/usr/bin/env python3
"""
Simple test script for the integrated API endpoints
"""

import requests
import json

def test_classroom_endpoints():
    """Test the classroom API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing Classroom API Endpoints")
    print("=" * 50)
    
    # Test 1: Get Google Classroom courses
    print("\n1. Testing /api/google-classroom-classes")
    try:
        response = requests.get(f"{base_url}/api/google-classroom-classes")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get students data
    print("\n2. Testing /api/classroom/students (GET)")
    try:
        response = requests.get(f"{base_url}/api/classroom/students")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Students found: {len(data.get('students', []))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Invite single student
    print("\n3. Testing /api/classroom/invite-student")
    try:
        payload = {
            "course_id": "772740435341",
            "email": "test-new-student@example.com"
        }
        response = requests.post(f"{base_url}/api/classroom/invite-student", 
                               json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Run LangGraph agent
    print("\n4. Testing /api/classroom/langgraph-agent")
    try:
        response = requests.post(f"{base_url}/api/classroom/langgraph-agent", 
                               json={})
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Agent Success: {result.get('success')}")
        if 'agent_result' in result:
            agent_result = result['agent_result']
            print(f"Students Processed: {len(agent_result.get('processed_students', []))}")
            print(f"Errors: {len(agent_result.get('errors', []))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Make sure the backend server is running first!")
    print("Run: python backend_server.py")
    input("Press Enter when server is ready...")
    test_classroom_endpoints()