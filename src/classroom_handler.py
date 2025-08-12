#!/usr/bin/env python3
"""
Google Classroom API handler for the Milesridge Education App.
This module provides functions to interact with the Google Classroom API.
"""

import os
import yaml
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.rosters',
    'https://www.googleapis.com/auth/classroom.rosters.readonly'
]

def load_config():
    """
    Load configuration from config.yml.
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config.yml: {e}")
        return None

def get_credentials():
    """
    Get valid user credentials from storage.
    
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    
    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if service account credentials are available
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                creds = service_account.Credentials.from_service_account_file(
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=SCOPES
                )
                subj = os.getenv("CLASSROOM_TEACHER_EMAIL")
                if subj:
                    creds = creds.with_subject(subj)
            else:
                # Try to use credentials.json for OAuth flow
                config = load_config()
                if config and 'google_classroom_credentials_file' in config:
                    credentials_file = os.path.join(os.path.dirname(__file__), '..', config['google_classroom_credentials_file'])
                    if os.path.exists(credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        print(f"Credentials file {credentials_file} not found.")
                        print("Please download OAuth credentials from Google Cloud Console.")
                        return None
                else:
                    print("No Google Classroom credentials found in config.yml or environment.")
                    print("Please set up authentication for Google Classroom API.")
                    return None
        
        # Save the credentials for the next run
        token_path = os.path.join(os.path.dirname(__file__), '..', 'token.pickle')
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_classroom_service():
    """
    Create and return a Google Classroom service object.
    """
    creds = get_credentials()
    if not creds:
        return None
    
    try:
        service = build('classroom', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building classroom service: {e}")
        return None

def list_courses():
    """
    List all Google Classroom courses available to the authenticated user.
    Returns a list of course objects.
    """
    service = get_classroom_service()
    if not service:
        return []
    
    try:
        # Call the Classroom API
        results = service.courses().list().execute()
        courses = results.get('courses', [])
        return courses
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def get_courses_count():
    """
    Get the number of Google Classroom courses.
    Returns the count as an integer.
    """
    courses = list_courses()
    return len(courses)

def display_courses():
    """
    Display all Google Classroom courses with details.
    """
    courses = list_courses()
    
    if not courses:
        print("No courses found.")
        return
    
    print("\nGoogle Classroom Courses:")
    print("------------------------")
    for course in courses:
        print(f"ID: {course['id']}")
        print(f"Name: {course['name']}")
        if 'section' in course:
            print(f"Section: {course['section']}")
        print(f"State: {course['courseState']}")
        print("------------------------")
    
    print(f"\nTotal number of courses: {len(courses)}")

def get_course_details(course_id):
    """
    Get detailed information about a specific course.
    
    Args:
        course_id: The ID of the course to get details for.
    
    Returns:
        A dictionary containing course details.
    """
    service = get_classroom_service()
    if not service:
        return None
    
    try:
        course = service.courses().get(id=course_id).execute()
        return course
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def invite_student(course_id, student_email):
    """
    Invite a student to a Google Classroom course.
    
    Args:
        course_id: The ID of the course to invite the student to.
        student_email: The email address of the student to invite.
    
    Returns:
        Dictionary containing success status and invitation details or error message.
    """
    service = get_classroom_service()
    if not service:
        return {"success": False, "error": "Failed to connect to Google Classroom service"}
    
    try:
        invitation_body = {
            'courseId': course_id,
            'userId': student_email,
            'role': 'STUDENT'
        }
        
        invitation = service.invitations().create(body=invitation_body).execute()
        
        return {
            "success": True,
            "invitation_id": invitation.get('id'),
            "course_id": course_id,
            "student_email": student_email,
            "message": f"Successfully invited {student_email} to course {course_id}"
        }
        
    except HttpError as error:
        error_details = error.error_details if hasattr(error, 'error_details') else []
        
        if error.resp.status == 409:
            return {
                "success": False,
                "error": "Invitation already exists",
                "student_email": student_email,
                "course_id": course_id
            }
        elif error.resp.status == 404:
            return {
                "success": False,
                "error": "Course not found or student email invalid",
                "student_email": student_email,
                "course_id": course_id
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {error.resp.status}: {str(error)}",
                "student_email": student_email,
                "course_id": course_id,
                "details": error_details
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "student_email": student_email,
            "course_id": course_id
        }

def invite_multiple_students(students_data):
    """
    Invite multiple students to Google Classroom courses.
    
    Args:
        students_data: List of dictionaries containing student information.
                      Each dict should have 'email', 'course_id', and optionally 'first_name', 'last_name'.
    
    Returns:
        Dictionary containing results summary and detailed results for each student.
    """
    results = []
    success_count = 0
    error_count = 0
    
    for student in students_data:
        if not all(key in student for key in ['email', 'course_id']):
            results.append({
                "success": False,
                "error": "Missing required fields (email, course_id)",
                "student_data": student
            })
            error_count += 1
            continue
        
        result = invite_student(student['course_id'], student['email'])
        result['student_name'] = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
        results.append(result)
        
        if result['success']:
            success_count += 1
        else:
            error_count += 1
    
    return {
        "summary": {
            "total_students": len(students_data),
            "successful_invitations": success_count,
            "failed_invitations": error_count,
            "success_rate": round((success_count / len(students_data)) * 100, 2) if students_data else 0
        },
        "results": results
    }

def create_quiz_assignment(course_id, quiz_data, due_date=None):
    """
    Create a quiz assignment in Google Classroom from JSON quiz data.
    
    Args:
        course_id: The ID of the course to create the assignment in.
        quiz_data: Dictionary containing quiz data (from quiz.json).
        due_date: Optional due date for the assignment (ISO format string).
    
    Returns:
        Dictionary containing success status and assignment details or error message.
    """
    service = get_classroom_service()
    if not service:
        return {"success": False, "error": "Failed to connect to Google Classroom service"}
    
    try:
        # Prepare assignment description with questions
        description = f"**{quiz_data.get('title', 'Quiz')}**\n\n"
        
        for i, question in enumerate(quiz_data.get('questions', []), 1):
            description += f"**Question {i}:** {question['question']}\n\n"
            
            if question.get('type') == 'multiple_choice_question' and question.get('options'):
                for j, option in enumerate(question['options'], 1):
                    # Mark correct answer with ✓
                    marker = " ✓" if option == question.get('answer') else ""
                    description += f"{chr(64+j)}. {option}{marker}\n"
                description += "\n"
        
        # Create coursework assignment
        assignment_body = {
            'title': quiz_data.get('title', 'Quiz Assignment'),
            'description': description,
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
            'maxPoints': len(quiz_data.get('questions', [])) * 10  # 10 points per question
        }
        
        # Add due date if provided
        if due_date:
            try:
                from datetime import datetime
                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                assignment_body['dueDate'] = {
                    'year': due_datetime.year,
                    'month': due_datetime.month,
                    'day': due_datetime.day
                }
                assignment_body['dueTime'] = {
                    'hours': due_datetime.hour,
                    'minutes': due_datetime.minute
                }
            except Exception as date_error:
                print(f"Warning: Invalid due date format: {date_error}")
        
        # Create the assignment
        assignment = service.courses().courseWork().create(
            courseId=course_id,
            body=assignment_body
        ).execute()
        
        return {
            "success": True,
            "assignment_id": assignment.get('id'),
            "course_id": course_id,
            "title": assignment.get('title'),
            "state": assignment.get('state'),
            "max_points": assignment.get('maxPoints'),
            "question_count": len(quiz_data.get('questions', [])),
            "alternate_link": assignment.get('alternateLink'),
            "message": f"Successfully created quiz assignment '{assignment.get('title')}' in course {course_id}"
        }
        
    except HttpError as error:
        if error.resp.status == 404:
            return {
                "success": False,
                "error": "Course not found",
                "course_id": course_id
            }
        elif error.resp.status == 403:
            return {
                "success": False,
                "error": "Insufficient permissions to create assignment",
                "course_id": course_id
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {error.resp.status}: {str(error)}",
                "course_id": course_id
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "course_id": course_id
        }

def upload_quiz_from_file(course_id, quiz_file_path="../data/quiz.json", due_date=None):
    """
    Load quiz from JSON file and create assignment in Google Classroom.
    
    Args:
        course_id: The ID of the course to create the assignment in.
        quiz_file_path: Path to the quiz JSON file.
        due_date: Optional due date for the assignment (ISO format string).
    
    Returns:
        Dictionary containing success status and assignment details or error message.
    """
    try:
        # Load quiz data from file
        quiz_file_path = os.path.join(os.path.dirname(__file__), quiz_file_path)
        
        if not os.path.exists(quiz_file_path):
            return {
                "success": False,
                "error": f"Quiz file not found: {quiz_file_path}"
            }
        
        with open(quiz_file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        # Validate quiz data
        if not quiz_data.get('questions'):
            return {
                "success": False,
                "error": "No questions found in quiz file"
            }
        
        # Create the quiz assignment
        result = create_quiz_assignment(course_id, quiz_data, due_date)
        result['quiz_file'] = quiz_file_path
        result['questions_loaded'] = len(quiz_data.get('questions', []))
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON in quiz file: {str(e)}",
            "quiz_file": quiz_file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error loading quiz file: {str(e)}",
            "quiz_file": quiz_file_path
        }

if __name__ == "__main__":
    # Display all courses when run directly
    display_courses()
