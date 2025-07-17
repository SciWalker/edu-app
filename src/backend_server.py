from flask import Flask, jsonify, request
import json
import os
from flask_cors import CORS
from database import db, init_db_with_config
from config import POSTGRES_CONFIG, FLASK_DEBUG, FLASK_HOST, FLASK_PORT

# Initialize database with PostgreSQL configuration
init_db_with_config(POSTGRES_CONFIG)

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

@app.route('/api/database/tables', methods=['GET'])
def get_database_tables():
    """Get a list of all tables in the database."""
    try:
        # Query to get all table names from PostgreSQL information schema
        tables = db.execute_query("""
            SELECT table_name as name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        return jsonify(tables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/table/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get all data from a specific table."""
    try:
        # Validate table name to prevent SQL injection
        valid_tables = [table['name'] for table in db.execute_query("""
            SELECT table_name as name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)]
        
        if table_name not in valid_tables:
            return jsonify({'error': f'Invalid table name: {table_name}'}), 400
        
        # Get table data
        data = db.execute_query(f"SELECT * FROM {table_name}")
        
        # Get table schema
        schema = db.execute_query(f"""
            SELECT 
                column_name as name,
                ordinal_position as cid,
                data_type as type,
                is_nullable as notnull,
                column_default as dflt_value,
                CASE 
                    WHEN constraint_type = 'PRIMARY KEY' THEN 1 
                    ELSE 0 
                END as pk
            FROM 
                information_schema.columns
            LEFT JOIN 
                information_schema.key_column_usage USING (column_name, table_name)
            LEFT JOIN 
                information_schema.table_constraints USING (constraint_name)
            WHERE 
                table_name = %s
            ORDER BY 
                ordinal_position
        """, (table_name,))
        
        return jsonify({
            'data': data,
            'schema': schema
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)