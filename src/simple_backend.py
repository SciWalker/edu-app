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

if __name__ == '__main__':
    print("🚀 Starting simplified edu-app backend...")
    print("📍 Available endpoints:")
    print("   GET  /health")
    print("   GET  /api/google-classroom-classes")
    print("   POST /api/classroom/upload-material")
    print("   POST /api/ocr/process")
    print("   POST /api/ocr/process-upload")
    print("   GET  /api/processed-data")
    print("   GET  /api/processed-data/<filename>")
    print("   GET  /api/lesson-plans")
    print("   GET  /api/quizzes")
    print("🌐 Server running on http://localhost:5000")
    print("🔗 Frontend should connect to http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)