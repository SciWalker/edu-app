#!/usr/bin/env python3
"""
Simplified backend server for the edu-app frontend.
Uses Google Classroom API directly without database dependencies.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
import tempfile
import uuid

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Global chatbot instances - now using LangGraph agent integration
chatbot_instances = {
    "gemini": None,
    "claude": None,
    "langgraph_gemini": None,
    "langgraph_claude": None
}
current_chatbot_type = "langgraph_gemini"  # Default to LangGraph with Gemini

@app.route('/api/google-classroom-classes', methods=['GET'])
def get_google_classroom_classes():
    """Get Google Classroom classes using the API."""
    try:
        # Import classroom handler
        import classroom_handler
        
        # Get classes from Google Classroom API
        classes = classroom_handler.list_courses()
        
        if not classes:
            return jsonify({
                "error": "No classes found or authentication failed",
                "classes": []
            }), 200
        
        # Format classes for frontend
        formatted_classes = []
        for cls in classes:
            formatted_classes.append({
                "id": cls.get("id", ""),
                "name": cls.get("name", "Unnamed Class"),
                "section": cls.get("section", ""),
                "description": cls.get("description", ""),
                "courseState": cls.get("courseState", "UNKNOWN"),
                "link": cls.get("alternateLink", ""),
                "teacherFolder": cls.get("teacherFolder", {}).get("title", "")
            })
        
        return jsonify(formatted_classes)
        
    except Exception as e:
        print(f"Error fetching classes: {e}")
        return jsonify({
            "error": str(e),
            "classes": []
        }), 500

@app.route('/api/classroom/upload-material', methods=['POST'])
def upload_material_to_classroom():
    """Upload OCR-extracted material to Google Classroom."""
    try:
        data = request.json
        course_id = data.get('courseId')
        material_data = data.get('materialData')
        
        if not course_id or not material_data:
            return jsonify({"error": "Missing courseId or materialData"}), 400
        
        # Import classroom uploader
        from ocr_module.classroom_uploader import OCRClassroomUploader
        
        uploader = OCRClassroomUploader()
        
        # Upload to classroom
        result = uploader.upload_to_classroom(
            course_id=course_id,
            ocr_data=material_data,
            assignment_type="material"
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/classroom/upload-quiz', methods=['POST'])
def upload_quiz_to_classroom():
    """Upload OCR-generated quiz to Google Classroom."""
    try:
        data = request.json
        course_id = data.get('courseId')
        quiz_data = data.get('quizData')
        
        if not course_id or not quiz_data:
            return jsonify({"error": "Missing courseId or quizData"}), 400
        
        # Import classroom uploader
        from ocr_module.classroom_uploader import OCRClassroomUploader
        
        uploader = OCRClassroomUploader()
        
        # Upload quiz to classroom as an assignment
        result = uploader.upload_to_classroom(
            course_id=course_id,
            ocr_data=quiz_data,
            assignment_type="quiz"
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ocr/process', methods=['POST'])
def process_ocr_image():
    """Process an image with OCR."""
    try:
        data = request.json
        image_path = data.get('imagePath')
        extraction_type = data.get('extractionType', 'educational_content')
        
        if not image_path:
            return jsonify({"error": "Missing imagePath"}), 400
        
        # Import OCR pipeline
        from ocr_module import OCRPipeline
        
        pipeline = OCRPipeline()
        result = pipeline.process_image(
            image_path=image_path,
            extraction_type=extraction_type,
            preprocess=True
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ocr/process-upload', methods=['POST'])
def process_uploaded_image():
    """Process an uploaded image file with OCR."""
    try:
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get extraction type from form data
        extraction_type = request.form.get('extractionType', 'educational_content')
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Invalid file type. Supported: PNG, JPG, JPEG, GIF, BMP, WebP"}), 400
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Save uploaded file with unique name
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = uploads_dir / unique_filename
        
        file.save(str(file_path))
        
        try:
            # Import and use OCR pipeline
            from ocr_module import OCRPipeline
            
            pipeline = OCRPipeline()
            result = pipeline.process_image(
                image_path=str(file_path),
                extraction_type=extraction_type,
                preprocess=True
            )
            
            # If extraction type is 'quiz', generate quiz using the OCR text
            if extraction_type == 'quiz' and result.get('pipeline_status') == 'success':
                result = generate_quiz_from_ocr(result)
            
            return jsonify(result)
            
        except Exception as ocr_error:
            return jsonify({
                "error": f"OCR processing failed: {str(ocr_error)}",
                "pipeline_status": "failed"
            }), 500
            
        finally:
            # Clean up uploaded file
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup uploaded file: {cleanup_error}")
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_quiz_from_ocr(ocr_result):
    """Generate quiz from OCR result using generate_quiz.py functions."""
    try:
        # Import the quiz generation functions
        sys.path.append(str(Path(__file__).parent))
        from generate_quiz import generate_quiz_with_gemini
        
        # Extract text from OCR result
        ocr_text = ocr_result.get('ocr_result', {}).get('text', '')
        
        # Create a lesson plan structure from OCR text
        lesson_plan = {
            'topic': ocr_result.get('extracted_data', {}).get('structured_data', {}).get('subject', 'General Knowledge'),
            'content': ocr_text,
            'number_of_questions': 5,  # Generate 5 questions minimum
            'response_type': 'multiple_choice_question'
        }
        
        # Generate quiz using Gemini
        quiz_data = generate_quiz_with_gemini(lesson_plan)
        
        # Update the OCR result with quiz data
        ocr_result['extracted_data']['structured_data'] = {
            **ocr_result.get('extracted_data', {}).get('structured_data', {}),
            'title': quiz_data.get('title', 'Generated Quiz'),
            'questions': quiz_data.get('questions', []),
            'quiz_type': 'multiple_choice',
            'content_source': 'ocr_generated'
        }
        
        # Update confidence score if quiz was generated successfully
        if quiz_data.get('questions'):
            ocr_result['extracted_data']['confidence_score'] = 0.9
        
        return ocr_result
        
    except Exception as e:
        print(f"Error generating quiz from OCR: {e}")
        # Return original result if quiz generation fails
        ocr_result['extracted_data']['errors'] = ocr_result.get('extracted_data', {}).get('errors', [])
        ocr_result['extracted_data']['errors'].append(f"Quiz generation failed: {str(e)}")
        return ocr_result

@app.route('/api/processed-data', methods=['GET'])
def get_processed_data():
    """Get list of processed OCR data files."""
    try:
        processed_dir = Path("processed_data")
        if not processed_dir.exists():
            return jsonify({"files": []})
        
        files = []
        for file_path in processed_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "title": data.get('structured_data', {}).get('title', 'Unknown'),
                    "subject": data.get('structured_data', {}).get('subject', 'Unknown'),
                    "timestamp": data.get('timestamp', ''),
                    "confidence": data.get('confidence_score', 0)
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return jsonify({"files": files})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/processed-data/<filename>', methods=['GET'])
def get_processed_file(filename):
    """Get specific processed OCR data file."""
    try:
        file_path = Path("processed_data") / filename
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Simplified edu-app backend is running"})

@app.route('/api/lesson-plans', methods=['GET'])
def get_lesson_plans():
    """Get lesson plans from local data files."""
    try:
        # Check if lesson plan file exists
        lesson_file = Path("data/lesson_plan.json")
        if lesson_file.exists():
            with open(lesson_file, 'r') as f:
                lesson_data = json.load(f)
            return jsonify([lesson_data])  # Return as array for frontend compatibility
        else:
            return jsonify([])  # Empty array if no data
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    """Get quizzes from local data files."""
    try:
        # Check if quiz file exists
        quiz_file = Path("data/quiz.json")
        if quiz_file.exists():
            with open(quiz_file, 'r') as f:
                quiz_data = json.load(f)
            return jsonify([quiz_data])  # Return as array for frontend compatibility
        else:
            return jsonify([])  # Empty array if no data
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    """Get single quiz from local data files."""
    try:
        # Check if quiz file exists
        quiz_file = Path("data/quiz.json")
        if quiz_file.exists():
            with open(quiz_file, 'r') as f:
                quiz_data = json.load(f)
            return jsonify(quiz_data)  # Return single object
        else:
            return jsonify({"error": "No quiz data found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
def save_quiz():
    """Save quiz data to local file."""
    try:
        quiz_data = request.json
        if not quiz_data:
            return jsonify({"error": "No quiz data provided"}), 400
            
        # Ensure data directory exists
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Save to quiz file
        quiz_file = data_dir / "quiz.json"
        with open(quiz_file, 'w') as f:
            json.dump(quiz_data, f, indent=2)
        
        return jsonify({"message": "Quiz saved successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_chatbot_instance(chatbot_type: str = None):
    """Get or create the chatbot instance."""
    global chatbot_instances, current_chatbot_type
    
    if chatbot_type is None:
        chatbot_type = current_chatbot_type
    
    if chatbot_instances[chatbot_type] is None:
        try:
            if chatbot_type == "gemini":
                from chatbot_module.gemini_chat import GeminiChatbot
                chatbot_instances[chatbot_type] = GeminiChatbot()
                print("✓ Gemini chatbot initialized")
            elif chatbot_type == "claude":
                from chatbot_module.claude_chat import ClaudeChatbot
                chatbot_instances[chatbot_type] = ClaudeChatbot()
                print("✓ Claude chatbot initialized")
            elif chatbot_type == "langgraph_gemini":
                from chatbot_module.gemini_chat import GeminiChatbot
                chatbot_instances[chatbot_type] = GeminiChatbot()
                print("✓ Gemini chatbot with LangGraph agent initialized")
            elif chatbot_type == "langgraph_claude":
                from chatbot_module.claude_chat import ClaudeChatbot
                chatbot_instances[chatbot_type] = ClaudeChatbot()
                print("✓ Claude chatbot with LangGraph agent initialized")
            else:
                raise ValueError(f"Unknown chatbot type: {chatbot_type}")
        except Exception as e:
            print(f"Warning: Could not initialize {chatbot_type} chatbot: {e}")
            chatbot_instances[chatbot_type] = None
    
    return chatbot_instances[chatbot_type]

@app.route('/api/chatbot/message', methods=['POST'])
def send_chatbot_message():
    """Send a message to the chatbot and get a response."""
    try:
        data = request.json
        message = data.get('message')
        user_id = data.get('user_id', 'anonymous')
        chatbot_type = data.get('chatbot_type', current_chatbot_type)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        chatbot = get_chatbot_instance(chatbot_type)
        if not chatbot:
            return jsonify({
                "success": False,
                "error": f"{chatbot_type.title()} chatbot is not available. Please check API configuration."
            }), 500
        
        result = chatbot.send_message(message, user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Chatbot error: {str(e)}"
        }), 500

@app.route('/api/chatbot/clear', methods=['POST'])
def clear_chatbot_conversation():
    """Clear the chatbot conversation history."""
    try:
        data = request.json if request.json else {}
        chatbot_type = data.get('chatbot_type', current_chatbot_type)
        
        chatbot = get_chatbot_instance(chatbot_type)
        if not chatbot:
            return jsonify({"error": f"{chatbot_type.title()} chatbot is not available"}), 500
        
        chatbot.clear_conversation()
        return jsonify({"success": True, "message": f"{chatbot_type.title()} conversation cleared"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/switch', methods=['POST'])
def switch_chatbot():
    """Switch between different chatbot models."""
    try:
        global current_chatbot_type
        data = request.json
        new_type = data.get('chatbot_type')
        
        valid_types = ['gemini', 'claude', 'langgraph_gemini', 'langgraph_claude']
        if new_type not in valid_types:
            return jsonify({"error": f"Invalid chatbot type. Must be one of {valid_types}"}), 400
        
        # Test if the new chatbot can be initialized
        test_chatbot = get_chatbot_instance(new_type)
        if not test_chatbot:
            return jsonify({
                "error": f"Could not initialize {new_type.title()} chatbot. Please check API configuration."
            }), 500
        
        current_chatbot_type = new_type
        return jsonify({
            "success": True,
            "message": f"Switched to {new_type.title()} chatbot",
            "current_chatbot": new_type
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/status', methods=['GET'])
def get_chatbot_status():
    """Get current chatbot status and available models."""
    try:
        status = {
            "current_chatbot": current_chatbot_type,
            "available_chatbots": [],
            "initialized_chatbots": []
        }
        
        # Check which chatbots are available - only show LangGraph versions
        priority_order = ["langgraph_gemini", "langgraph_claude"]
        
        for chatbot_type in priority_order:
            try:
                chatbot = get_chatbot_instance(chatbot_type)
                if chatbot:
                    status["available_chatbots"].append(chatbot_type)
                    if chatbot_instances[chatbot_type] is not None:
                        status["initialized_chatbots"].append(chatbot_type)
            except Exception as e:
                print(f"Chatbot {chatbot_type} not available: {e}")
                pass
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/history', methods=['GET'])
def get_chatbot_history():
    """Get the chatbot conversation history."""
    try:
        chatbot = get_chatbot_instance()
        if not chatbot:
            return jsonify({"error": "Chatbot is not available"}), 500
        
        history = chatbot.get_conversation_history()
        summary = chatbot.get_conversation_summary()
        
        return jsonify({
            "history": history,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/export', methods=['POST'])
def export_chatbot_conversation():
    """Export the chatbot conversation to a file."""
    try:
        chatbot = get_chatbot_instance()
        if not chatbot:
            return jsonify({"error": "Chatbot is not available"}), 500
        
        file_path = chatbot.export_conversation()
        return jsonify({
            "success": True,
            "file_path": file_path,
            "message": f"Conversation exported to {file_path}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting simplified edu-app backend...")
    print("📍 Available endpoints:")
    print("   GET  /health")
    print("   GET  /api/google-classroom-classes")
    print("   POST /api/classroom/upload-material")
    print("   POST /api/classroom/upload-quiz")
    print("   POST /api/ocr/process")
    print("   POST /api/ocr/process-upload")
    print("   GET  /api/processed-data")
    print("   GET  /api/processed-data/<filename>")
    print("   GET  /api/lesson-plans")
    print("   GET  /api/quizzes")
    print("   GET  /api/quiz")
    print("   POST /api/quiz")
    print("   POST /api/chatbot/message")
    print("   POST /api/chatbot/clear")
    print("   POST /api/chatbot/switch")
    print("   GET  /api/chatbot/status")
    print("   GET  /api/chatbot/history")
    print("   POST /api/chatbot/export")
    print("🌐 Server running on http://localhost:5000")
    print("🔗 Frontend should connect to http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)