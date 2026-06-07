#!/usr/bin/env python3
"""
Google Classroom API Authentication Checker
This script tests your current Google Classroom API permissions and access level.
"""

import os
import sys
from pathlib import Path
import classroom_handler

def check_authentication():
    """Check Google Classroom API authentication and permissions."""
    print("🔍 Checking Google Classroom API Authentication...")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Environment Variables Check:")
    print("-" * 30)
    
    google_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    teacher_email = os.environ.get("CLASSROOM_TEACHER_EMAIL")
    
    if google_creds:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
        if os.path.exists(google_creds):
            print(f"✅ Credentials file exists: {google_creds}")
        else:
            print(f"❌ Credentials file NOT found: {google_creds}")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
    
    if teacher_email:
        print(f"✅ CLASSROOM_TEACHER_EMAIL: {teacher_email}")
    else:
        print("❌ CLASSROOM_TEACHER_EMAIL not set")
    
    # Check service connection
    print("\n2. Google Classroom Service Connection:")
    print("-" * 40)
    
    try:
        service = classroom_handler.get_classroom_service()
        if service:
            print("✅ Successfully connected to Google Classroom API")
            
            # Test basic API access
            print("\n3. API Access Test:")
            print("-" * 20)
            
            try:
                # Try to list courses
                courses = classroom_handler.list_courses()
                print(f"✅ Can list courses: Found {len(courses)} courses")
                
                if courses:
                    print("\nYour courses:")
                    for i, course in enumerate(courses[:5], 1):  # Show first 5 courses
                        print(f"  {i}. {course.get('name', 'Unnamed')} (ID: {course.get('id', 'Unknown')})")
                        print(f"     State: {course.get('courseState', 'Unknown')}")
                        print(f"     Role: {course.get('teacherFolder', {}).get('title', 'Unknown role')}")
                    
                    if len(courses) > 5:
                        print(f"     ... and {len(courses) - 5} more courses")
                
            except Exception as e:
                print(f"❌ Cannot list courses: {e}")
            
            # Test course creation permissions
            print("\n4. Course Creation Permission Test:")
            print("-" * 35)
            
            try:
                # Try to create a test course (will fail if no permissions)
                test_result = classroom_handler.create_course(
                    "AUTH_TEST_COURSE_DELETE_ME", 
                    "TEST", 
                    "This is a test course to check permissions - please delete"
                )
                
                if test_result.get("success"):
                    print("✅ COURSE CREATION ALLOWED - You can create courses!")
                    course_id = test_result.get("course_id")
                    print(f"   Test course created with ID: {course_id}")
                    
                    # Try to delete the test course
                    try:
                        service.courses().delete(id=course_id).execute()
                        print("✅ Test course deleted successfully")
                    except Exception as delete_error:
                        print(f"⚠️  Test course created but couldn't delete: {delete_error}")
                        print(f"   Please manually delete course ID: {course_id}")
                        
                else:
                    error = test_result.get("error", "Unknown error")
                    if "403" in str(error) or "Insufficient permissions" in str(error):
                        print("❌ COURSE CREATION NOT ALLOWED - Insufficient permissions")
                        print("   You can manage existing courses but cannot create new ones")
                    else:
                        print(f"❌ Course creation test failed: {error}")
                        
            except Exception as e:
                print(f"❌ Course creation test error: {e}")
            
            # Test invitation permissions
            print("\n5. Student Invitation Permission Test:")
            print("-" * 37)
            
            if courses:
                test_course_id = courses[0].get('id')
                print(f"Testing with course: {courses[0].get('name', 'Unknown')} ({test_course_id})")
                
                try:
                    # Try to create an invitation (but don't send it)
                    invitation_result = classroom_handler.invite_student(
                        test_course_id, 
                        "test@example.com"  # This won't work but will test permissions
                    )
                    
                    if invitation_result.get("success"):
                        print("✅ STUDENT INVITATIONS ALLOWED")
                    else:
                        error = invitation_result.get("error", "Unknown error")
                        if "403" in str(error):
                            print("❌ STUDENT INVITATIONS NOT ALLOWED - Insufficient permissions")
                        elif "404" in str(error) or "invalid" in str(error).lower():
                            print("✅ STUDENT INVITATIONS ALLOWED (test email invalid as expected)")
                        else:
                            print(f"? Student invitation test unclear: {error}")
                            
                except Exception as e:
                    print(f"❌ Student invitation test error: {e}")
            else:
                print("❌ Cannot test invitations - no courses found")
        
        else:
            print("❌ Failed to connect to Google Classroom API")
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
    
    # Account type detection
    print("\n6. Account Type Detection:")
    print("-" * 27)
    
    if teacher_email:
        domain = teacher_email.split('@')[1] if '@' in teacher_email else 'Unknown'
        print(f"Email domain: {domain}")
        
        if domain.endswith('.edu') or 'school' in domain.lower():
            print("✅ Likely Google Workspace for Education account")
        elif domain == 'gmail.com':
            print("❌ Regular Gmail account - limited Classroom API access")
        else:
            print("? Custom domain - may or may not have education features")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    service = classroom_handler.get_classroom_service()
    if service:
        courses = classroom_handler.list_courses()
        print(f"✅ API Connection: Working")
        print(f"✅ Course Access: Can access {len(courses)} courses")
        
        # Test course creation one more time for summary
        test_result = classroom_handler.create_course("TEMP_AUTH_TEST", "TEST", "Permission test")
        if test_result.get("success"):
            print(f"✅ Course Creation: ALLOWED")
            # Clean up
            try:
                service.courses().delete(id=test_result.get("course_id")).execute()
            except:
                pass
        else:
            print(f"❌ Course Creation: NOT ALLOWED")
            
    else:
        print(f"❌ API Connection: Failed")
    
    print("\nRecommendations:")
    if not service:
        print("- Check your Google Cloud credentials and permissions")
    elif not courses:
        print("- Make sure you have access to at least one Google Classroom course")
    else:
        print("- Your authentication is working for existing course management")
        print("- For course creation, contact your Google Workspace administrator")


if __name__ == "__main__":
    check_authentication()