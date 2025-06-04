import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Supabase client
from config.supabase import get_supabase

def create_tables():
    """Create necessary tables if they don't exist"""
    supabase = get_supabase()
    
    # Create teachers table
    supabase.table('teachers').create({
        'teacher_id': {'type': 'int8', 'primaryKey': True, 'identity': {'generationStrategy': 'BY DEFAULT'}},
        'first_name': {'type': 'varchar', 'notNull': True},
        'last_name': {'type': 'varchar', 'notNull': True},
        'email': {'type': 'varchar', 'notNull': True, 'unique': True},
        'created_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}},
        'updated_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}}
    })
    print("Created teachers table")
    
    # Create students table
    supabase.table('students').create({
        'student_id': {'type': 'int8', 'primaryKey': True, 'identity': {'generationStrategy': 'BY DEFAULT'}},
        'first_name': {'type': 'varchar', 'notNull': True},
        'last_name': {'type': 'varchar', 'notNull': True},
        'email': {'type': 'varchar', 'notNull': True, 'unique': True},
        'date_of_birth': {'type': 'date'},
        'created_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}},
        'updated_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}}
    })
    print("Created students table")
    
    # Create classes table
    supabase.table('classes').create({
        'class_id': {'type': 'int8', 'primaryKey': True, 'identity': {'generationStrategy': 'BY DEFAULT'}},
        'class_name': {'type': 'varchar', 'notNull': True},
        'academic_year': {'type': 'varchar', 'notNull': True},
        'semester': {'type': 'varchar', 'notNull': True},
        'description': {'type': 'text'},
        'created_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}},
        'updated_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}}
    })
    print("Created classes table")
    
    # Create student_class table
    supabase.table('student_class').create({
        'student_id': {'type': 'int8', 'notNull': True, 'references': {'table': 'students', 'column': 'student_id'}},
        'class_id': {'type': 'int8', 'notNull': True, 'references': {'table': 'classes', 'column': 'class_id'}},
        'enrollment_date': {'type': 'date', 'notNull': True},
        'status': {'type': 'varchar', 'default': {'type': 'literal', 'value': 'active'}},
        'created_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}}
    }, {'primaryKey': ['student_id', 'class_id']})
    print("Created student_class table")
    
    # Create class_teacher table
    supabase.table('class_teacher').create({
        'teacher_id': {'type': 'int8', 'notNull': True, 'references': {'table': 'teachers', 'column': 'teacher_id'}},
        'class_id': {'type': 'int8', 'notNull': True, 'references': {'table': 'classes', 'column': 'class_id'}},
        'is_primary': {'type': 'boolean', 'default': {'type': 'literal', 'value': False}},
        'created_at': {'type': 'timestamp', 'default': {'type': 'expression', 'value': 'now()'}}
    }, {'primaryKey': ['teacher_id', 'class_id']})
    print("Created class_teacher table")

def seed_database():
    """Seed the database with example data"""
    supabase = get_supabase()
    
    # Insert teachers
    teachers = [
        {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com'},
        {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@example.com'}
    ]
    
    inserted_teachers = []
    for teacher in teachers:
        # Check if teacher already exists
        existing = supabase.table('teachers').select('*').eq('email', teacher['email']).execute()
        if existing.data:
            inserted_teachers.append(existing.data[0])
            print(f"Teacher {teacher['email']} already exists")
        else:
            result = supabase.table('teachers').insert(teacher).execute()
            inserted_teachers.append(result.data[0])
            print(f"Added teacher: {teacher['email']}")
    
    # Insert students
    students = [
        {'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice.j@example.com', 'date_of_birth': '2010-05-15'},
        {'first_name': 'Bob', 'last_name': 'Williams', 'email': 'bob.w@example.com', 'date_of_birth': '2010-08-22'},
        {'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie.b@example.com', 'date_of_birth': '2011-02-10'},
        {'first_name': 'Diana', 'last_name': 'Miller', 'email': 'diana.m@example.com', 'date_of_birth': '2010-11-30'},
        {'first_name': 'Ethan', 'last_name': 'Davis', 'email': 'ethan.d@example.com', 'date_of_birth': '2011-01-20'}
    ]
    
    inserted_students = []
    for student in students:
        # Check if student already exists
        existing = supabase.table('students').select('*').eq('email', student['email']).execute()
        if existing.data:
            inserted_students.append(existing.data[0])
            print(f"Student {student['email']} already exists")
        else:
            result = supabase.table('students').insert(student).execute()
            inserted_students.append(result.data[0])
            print(f"Added student: {student['email']}")
    
    # Insert a class
    class_data = {
        'class_name': 'Mathematics 101',
        'academic_year': '2024-2025',
        'semester': 'Spring',
        'description': 'Introductory Mathematics for Beginners'
    }
    
    # Check if class already exists
    existing_class = supabase.table('classes').select('*').eq('class_name', class_data['class_name']).execute()
    if existing_class.data:
        class_record = existing_class.data[0]
        print(f"Class {class_data['class_name']} already exists")
    else:
        class_result = supabase.table('classes').insert(class_data).execute()
        class_record = class_result.data[0]
        print(f"Added class: {class_data['class_name']}")
    
    # Enroll all students in the class
    for student in inserted_students:
        enrollment = {
            'student_id': student['student_id'],
            'class_id': class_record['class_id'],
            'enrollment_date': date.today().isoformat(),
            'status': 'active'
        }
        # Check if enrollment exists
        existing_enrollment = supabase.table('student_class')\
            .select('*')\
            .eq('student_id', student['student_id'])\
            .eq('class_id', class_record['class_id'])\
            .execute()
        
        if not existing_enrollment.data:
            supabase.table('student_class').insert(enrollment).execute()
            print(f"Enrolled student {student['first_name']} in class {class_record['class_name']}")
    
    # Assign teachers to the class
    for teacher in inserted_teachers:
        assignment = {
            'teacher_id': teacher['teacher_id'],
            'class_id': class_record['class_id'],
            'is_primary': True if teacher['email'] == 'john.smith@example.com' else False
        }
        # Check if assignment exists
        existing_assignment = supabase.table('class_teacher')\
            .select('*')\
            .eq('teacher_id', teacher['teacher_id'])\
            .eq('class_id', class_record['class_id'])\
            .execute()
        
        if not existing_assignment.data:
            supabase.table('class_teacher').insert(assignment).execute()
            print(f"Assigned teacher {teacher['first_name']} to class {class_record['class_name']}")
    
    print("\nDatabase seeding completed successfully!")

if __name__ == "__main__":
    try:
        print("Creating tables...")
        create_tables()
        print("\nSeeding database...")
        seed_database()
    except Exception as e:
        print(f"Error: {e}")

