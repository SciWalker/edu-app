from flask import Flask, jsonify, request
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

LESSON_PLAN_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lesson_plan.json')
QUIZ_PATH = os.path.join(os.path.dirname(__file__), 'data', 'quiz.json')

@app.route('/api/lesson-plan', methods=['GET'])
def get_lesson_plan():
    try:
        with open(LESSON_PLAN_PATH, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lesson-plan', methods=['POST'])
def update_lesson_plan():
    try:
        data = request.json
        with open(LESSON_PLAN_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    try:
        with open(QUIZ_PATH, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
def update_quiz():
    try:
        data = request.json
        with open(QUIZ_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        import subprocess
        result = subprocess.run([
            'python', 'generate_quiz.py'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            # Load the generated quiz
            with open(QUIZ_PATH, 'r') as f:
                quiz = json.load(f)
            return jsonify({'success': True, 'quiz': quiz, 'llm_output': result.stdout})
        else:
            return jsonify({'error': f'LLM script failed: {result.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/google-classroom-classes', methods=['GET'])
def google_classroom_classes():
    try:
        # Import the classroom handler to use real Google Classroom API
        import classroom_handler
        
        # Get real classes from Google Classroom API
        classes = classroom_handler.list_courses()
        
        # If no classes are returned (e.g., authentication failed), return sample data
        if not classes:
            # Fallback to sample classes
            sample_classes = [
                {"id": "class1", "name": "Physics 101"},
                {"id": "class2", "name": "Chemistry 201"}
            ]
            return jsonify(sample_classes)
        
        # Format the classes for the frontend
        formatted_classes = []
        for cls in classes:
            formatted_classes.append({
                "id": cls.get("id", "unknown"),
                "name": cls.get("name", "Unnamed Class"),
                "description": cls.get("description", ""),
                "courseState": cls.get("courseState", ""),
                "link": cls.get("alternateLink", "")
            })
        
        return jsonify(formatted_classes)
    except Exception as e:
        print(f"Error fetching Google Classroom classes: {e}")
        # Return sample data as fallback
        sample_classes = [
            {"id": "class1", "name": "Physics 101"},
            {"id": "class2", "name": "Chemistry 201"}
        ]
        return jsonify(sample_classes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')