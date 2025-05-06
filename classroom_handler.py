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
    'https://www.googleapis.com/auth/classroom.rosters.readonly'
]

def load_config():
    """
    Load configuration from config.yml.
    """
    try:
        with open("config.yml", "r") as file:
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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
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
                    credentials_file = config['google_classroom_credentials_file']
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
        with open('token.pickle', 'wb') as token:
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

if __name__ == "__main__":
    # Display all courses when run directly
    display_courses()
