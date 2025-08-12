#!/usr/bin/env python3
"""
Script to upload quiz.json to Google Classroom
"""

import sys
import os
from classroom_handler import list_courses, upload_quiz_from_file

def main():
    """Main function to upload quiz to Google Classroom"""
    
    # First, let's list available courses
    print("Available Google Classroom Courses:")
    print("=" * 50)
    courses = list_courses()
    
    if not courses:
        print("No courses found. Please ensure you have access to Google Classroom courses.")
        return
    
    # Display courses with numbers for selection
    for i, course in enumerate(courses, 1):
        print(f"{i}. ID: {course['id']} - Name: {course['name']} - State: {course['courseState']}")
    
    # Get course selection from user
    try:
        if len(sys.argv) > 1:
            # Course ID provided as command line argument
            course_id = sys.argv[1]
        else:
            # Interactive selection
            choice = input(f"\nEnter course number (1-{len(courses)}) or course ID: ").strip()
            
            # Check if it's a number (course selection) or course ID
            if choice.isdigit() and 1 <= int(choice) <= len(courses):
                course_id = courses[int(choice) - 1]['id']
            else:
                course_id = choice
        
        print(f"\nUploading quiz to course ID: {course_id}")
        
        # Upload the quiz
        result = upload_quiz_from_file(course_id)
        
        if result['success']:
            print("SUCCESS: Quiz uploaded successfully!")
            print(f"Assignment ID: {result['assignment_id']}")
            print(f"Title: {result['title']}")
            print(f"Questions loaded: {result['questions_loaded']}")
            print(f"Max points: {result['max_points']}")
            if 'alternate_link' in result:
                print(f"Link: {result['alternate_link']}")
        else:
            print("FAILED: Failed to upload quiz:")
            print(f"Error: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nERROR: An error occurred: {str(e)}")

if __name__ == "__main__":
    main()