#!/usr/bin/env python3
"""
Simplified Flask server for testing classroom and LangGraph integration
"""

from flask import Flask, jsonify, request
import json
import os
from flask_cors import CORS
import classroom_handler
from langgraph_agent import GoogleClassroomAgent

app = Flask(__name__)
CORS(app)

@app.route('/api/classroom/courses', methods=['GET'])
def get_google_classroom_courses():
    """Get Google Classroom courses."""
    try:
        courses = classroom_handler.list_courses()
        
        if not courses:
            return jsonify({'error': 'No courses found or authentication failed'}), 404
        
        # Format the courses for the frontend
        formatted_courses = []
        for cls in courses:
            formatted_courses.append({
                "id": cls.get("id", "unknown"),
                "name": cls.get("name", "Unnamed Class"),
                "description": cls.get("description", ""),
                "courseState": cls.get("courseState", ""),
                "section": cls.get("section", ""),
                "enrollmentCode": cls.get("enrollmentCode", ""),
                "link": cls.get("alternateLink", "")
            })
        
        return jsonify(formatted_courses)
    except Exception as e:
        print(f"Error fetching Google Classroom courses: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/invite-student', methods=['POST'])
def invite_single_student():
    """Invite a single student to a Google Classroom course."""
    try:
        data = request.json
        
        # Validate required fields
        if not all(key in data for key in ['course_id', 'email']):
            return jsonify({'error': 'Missing required fields: course_id, email'}), 400
        
        result = classroom_handler.invite_student(data['course_id'], data['email'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/invite-multiple', methods=['POST'])
def invite_multiple_students():
    """Invite multiple students to Google Classroom courses."""
    try:
        data = request.json
        
        # Validate that students data is provided
        if 'students' not in data or not isinstance(data['students'], list):
            return jsonify({'error': 'Missing or invalid students data'}), 400
        
        result = classroom_handler.invite_multiple_students(data['students'])
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/langgraph-agent', methods=['POST'])
def run_langgraph_agent():
    """Run the LangGraph agent to process students from JSON and invite them to courses."""
    try:
        # Optional: accept custom JSON file path
        data = request.json or {}
        json_file_path = data.get('json_file_path', None)
        
        # Create and run the agent
        agent = GoogleClassroomAgent()
        result = agent.run(json_file_path)
        
        return jsonify({
            'success': True,
            'agent_result': result,
            'message': 'LangGraph agent completed successfully'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'LangGraph agent failed'
        }), 500

@app.route('/api/classroom/students', methods=['GET'])
def get_students_data():
    """Get the current students data from the JSON file."""
    try:
        students_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'students.json')
        
        if not os.path.exists(students_file):
            return jsonify({'error': 'Students data file not found'}), 404
        
        with open(students_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/students', methods=['POST'])
def update_students_data():
    """Update the students data in the JSON file."""
    try:
        data = request.json
        
        if 'students' not in data:
            return jsonify({'error': 'Missing students data'}), 400
        
        students_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'students.json')
        
        with open(students_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Students data updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/upload-quiz', methods=['POST'])
def upload_quiz_to_classroom():
    """Upload quiz from JSON file to Google Classroom as assignment."""
    try:
        data = request.json or {}
        
        # Validate required fields
        if 'course_id' not in data:
            return jsonify({'error': 'Missing required field: course_id'}), 400
        
        course_id = data['course_id']
        quiz_file_path = data.get('quiz_file_path', '../data/quiz.json')
        due_date = data.get('due_date', None)  # ISO format string, optional
        
        result = classroom_handler.upload_quiz_from_file(course_id, quiz_file_path, due_date)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classroom/create-quiz', methods=['POST'])
def create_quiz_assignment():
    """Create quiz assignment in Google Classroom from provided quiz data."""
    try:
        data = request.json
        
        # Validate required fields
        if not all(key in data for key in ['course_id', 'quiz_data']):
            return jsonify({'error': 'Missing required fields: course_id, quiz_data'}), 400
        
        course_id = data['course_id']
        quiz_data = data['quiz_data']
        due_date = data.get('due_date', None)  # ISO format string, optional
        
        result = classroom_handler.create_quiz_assignment(course_id, quiz_data, due_date)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Google Classroom LangGraph API'})

if __name__ == '__main__':
    print("Starting Google Classroom LangGraph API Server...")
    print("Available endpoints:")
    print("  GET  /api/classroom/courses - List Google Classroom courses")
    print("  POST /api/classroom/invite-student - Invite single student")
    print("  POST /api/classroom/invite-multiple - Invite multiple students")
    print("  POST /api/classroom/langgraph-agent - Run LangGraph agent")
    print("  GET  /api/classroom/students - Get students data")
    print("  POST /api/classroom/students - Update students data")
    print("  POST /api/classroom/upload-quiz - Upload quiz from JSON file")
    print("  POST /api/classroom/create-quiz - Create quiz from provided data")
    print("  GET  /health - Health check")
    print("\nServer running at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)