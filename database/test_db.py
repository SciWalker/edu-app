#!/usr/bin/env python3
"""
Test script for the database module.
This script demonstrates how to use the database module to perform CRUD operations.
"""
import os
import sys
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db

def cleanup_test_data():
    """Clean up test data from the database."""
    try:
        # Delete performance records first due to foreign key constraints
        db.execute_query("""
            DELETE FROM student_subject_performance 
            WHERE student_id IN (SELECT student_id FROM students WHERE email LIKE '%@example.com')
        """)
        
        # Delete enrollments
        db.execute_query("""
            DELETE FROM student_class 
            WHERE student_id IN (SELECT student_id FROM students WHERE email LIKE '%@example.com')
        """)
        
        # Delete teacher assignments
        db.execute_query("""
            DELETE FROM teacher_subject_class 
            WHERE teacher_id IN (SELECT teacher_id FROM teachers WHERE email LIKE '%@example.com')
        """)
        
        # Delete test students, teachers, classes, and subjects
        db.execute_query("DELETE FROM students WHERE email LIKE '%@example.com'")
        db.execute_query("DELETE FROM teachers WHERE email LIKE '%@example.com'")
        db.execute_query("DELETE FROM classes WHERE class_name LIKE 'Test Class%'")
        db.execute_query("DELETE FROM subjects WHERE subject_name LIKE 'Test Subject%'")
        
        print("Cleaned up test data successfully.")
    except Exception as e:
        print(f"Error cleaning up test data: {e}")
        raise

def print_header(title):
    """Print a section header."""
    print(f"\n{'=' * 50}")
    print(f"{title.upper()}")
    print(f"{'=' * 50}")

def test_database(clean_first=False):
    """Test the database functionality.
    
    Args:
        clean_first: If True, clean up test data before running tests
    """
    if clean_first:
        cleanup_test_data()
    
    try:
        # Add a teacher
        print_header("Adding a teacher")
        teacher_email = "john.doe@example.com"
        
        # Check if teacher already exists
        existing_teacher = db.execute_query(
            "SELECT teacher_id FROM teachers WHERE email = ?", 
            (teacher_email,),
            fetch_all=False
        )
        
        if existing_teacher:
            teacher_id = existing_teacher['teacher_id']
            print(f"Using existing teacher with ID: {teacher_id}")
        else:
            teacher_id = db.add_teacher("John", "Doe", teacher_email)
            print(f"Added teacher with ID: {teacher_id}")
        
        # Get the teacher
        teacher = db.get_teacher(teacher_id)
        print(f"Retrieved teacher: {teacher}")
        
        # Add a subject
        print_header("Adding a subject")
        subject_name = "Test Subject - Mathematics"
        subject_code = "TMATH101"
        
        # Check if subject already exists by name or code
        existing_subject = db.execute_query(
            "SELECT subject_id, subject_code FROM subjects WHERE subject_name = ? OR subject_code = ?",
            (subject_name, subject_code),
            fetch_all=False
        )
        
        if existing_subject:
            subject_id = existing_subject['subject_id']
            print(f"Using existing subject with ID: {subject_id}")
        else:
            # Generate a unique code with timestamp to avoid conflicts
            import time
            unique_code = f"TMATH{int(time.time()) % 10000}"
            subject_id = db.add_subject(subject_name, unique_code, "Introduction to Mathematics")
            print(f"Added subject with ID: {subject_id} and code: {unique_code}")
        
        # Add a class
        print_header("Adding a class")
        class_name = "Test Class 10A"
        existing_class = db.execute_query(
            "SELECT class_id FROM classes WHERE class_name = ? AND academic_year = ? AND semester = ?",
            (class_name, "2024-2025", "Spring"),
            fetch_all=False
        )
        
        if existing_class:
            class_id = existing_class['class_id']
            print(f"Using existing class with ID: {class_id}")
        else:
            class_id = db.add_class(class_name, "2024-2025", "Spring", "Test 10th Grade Class A")
            print(f"Added class with ID: {class_id}")
        
        # Assign teacher to class and subject
        print_header("Assigning teacher to class and subject")
        assignment_id = db.assign_teacher_to_class_subject(
            teacher_id, subject_id, class_id, "2024-2025", "Spring"
        )
        print(f"Assigned teacher to class and subject with ID: {assignment_id}")
        
        # Add a student
        print_header("Adding a student")
        student_email = "alice.smith@example.com"
        existing_student = db.execute_query(
            "SELECT student_id FROM students WHERE email = ?",
            (student_email,),
            fetch_all=False
        )
        
        if existing_student:
            student_id = existing_student['student_id']
            print(f"Using existing student with ID: {student_id}")
        else:
            student_id = db.add_student("Alice", "Smith", student_email, "2010-05-15")
            print(f"Added student with ID: {student_id}")
        
        # Enroll student in class
        print_header("Enrolling student in class")
        existing_enrollment = db.execute_query(
            "SELECT enrollment_id FROM student_class WHERE student_id = ? AND class_id = ?",
            (student_id, class_id),
            fetch_all=False
        )
        
        if existing_enrollment:
            enrollment_id = existing_enrollment['enrollment_id']
            print(f"Using existing enrollment with ID: {enrollment_id}")
        else:
            enrollment_id = db.enroll_student_in_class(student_id, class_id)
            print(f"Enrolled student in class with ID: {enrollment_id}")
        
        # Record student performance
        print_header("Recording student performance")
        performance_id = db.record_student_performance(
            student_id, subject_id, class_id, "2024-2025", "Spring", 
            score=85.5, grade="B+", attendance=95
        )
        print(f"Recorded student performance with ID: {performance_id}")
        
        # Get student report
        print_header("Generating student report")
        report = db.get_student_report(student_id)
        if report:
            print(f"Student: {report['student']['first_name']} {report['student']['last_name']}")
            print("\nClasses:")
            for cls in report['classes']:
                print(f"- {cls['class_name']} (Status: {cls['status']})")
            
            print("\nPerformance:")
            for perf in report['performance']:
                print(f"- {perf['subject_name']}: {perf['score']} ({perf['grade']}), "
                      f"Attendance: {perf['attendance']}%")
    
    except Exception as e:
        print(f"Error during test: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the database functionality')
    parser.add_argument('--clean', action='store_true', help='Clean up test data before running tests')
    args = parser.parse_args()
    
    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    try:
        # Run the test
        test_database(clean_first=args.clean)
    finally:
        # Always close the database connection
        db.close()
