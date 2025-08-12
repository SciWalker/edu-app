#!/usr/bin/env python3
"""
Quick script to list available Google Classroom courses
"""

import yaml
import pickle
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config.yml: {e}")
        return None


def get_oauth_credentials(credentials_file):
    """Get OAuth credentials from file and token cache"""
    scopes = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.students',
        'https://www.googleapis.com/auth/classroom.rosters',
        'https://www.googleapis.com/auth/classroom.rosters.readonly'
    ]
    
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
            if os.path.exists(credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes)
                creds = flow.run_local_server(port=0)
            else:
                print(f"OAuth credentials file {credentials_file} not found.")
                return None
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def list_courses():
    """List all available Google Classroom courses"""
    config = load_config()
    if not config:
        print("Failed to load config.yml")
        return
    
    credentials_file = config.get('google_classroom_credentials_file')
    if not credentials_file:
        print("No credentials file specified in config.yml")
        return
    
    try:
        creds = get_oauth_credentials(credentials_file)
        if not creds:
            print("Failed to get OAuth credentials")
            return
        
        service = build('classroom', 'v1', credentials=creds)
        
        # List courses
        results = service.courses().list().execute()
        courses = results.get('courses', [])
        
        if not courses:
            print("No courses found.")
            return
        
        print("\nAvailable Google Classroom Courses:")
        print("=" * 50)
        for course in courses:
            print(f"ID: {course['id']}")
            print(f"Name: {course['name']}")
            if 'section' in course:
                print(f"Section: {course['section']}")
            print(f"State: {course['courseState']}")
            if 'teacherFolder' in course:
                print(f"Teacher Folder: {course['teacherFolder']['title']}")
            print("-" * 30)
        
        print(f"\nTotal courses: {len(courses)}")
        
    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
    except Exception as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    list_courses()