import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Tuple

class Database:
    def __init__(self, db_config: Dict[str, str] = None):
        """Initialize the database connection.
        
        Args:
            db_config: Dictionary with PostgreSQL connection parameters
        """
        # Default configuration for PostgreSQL
        self.db_config = db_config or {
            'dbname': os.environ.get('POSTGRES_DB', 'edu_app'),
            'user': os.environ.get('POSTGRES_USER', 'postgres'),
            'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('POSTGRES_PORT', '5432')
        }
        
        self.conn = None
        self.connect()
        self.initialize_database()
    
    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            # Set autocommit to False for transaction control
            self.conn.autocommit = False
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Initialize the database by creating tables if they don't exist."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(schema_sql)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error initializing database: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = (), fetch_all: bool = True):
        """Execute a SQL query and return the results.
        
        Args:
            query: SQL query string
            params: Tuple of parameters for the query
            fetch_all: If True, fetch all results; if False, fetch one result
            
        Returns:
            List of dictionaries (rows) or a single row dictionary
        """
        try:
            # Use DictCursor to return results as dictionaries
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.conn.commit()
                if 'INSERT' in query.upper() and cursor.rowcount > 0:
                    # For PostgreSQL, we need to use RETURNING clause to get the inserted ID
                    # But if the query doesn't have it, we'll just return rowcount
                    if 'RETURNING' in query.upper():
                        row = cursor.fetchone()
                        return row[0] if row else cursor.rowcount
                    return cursor.rowcount
                return cursor.rowcount
            
            if fetch_all:
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            else:
                row = cursor.fetchone()
                result = dict(row) if row else None
                
            return result
            
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Database error: {e}")
            raise
    
    # Teacher methods
    def add_teacher(self, first_name: str, last_name: str, email: str) -> int:
        """Add a new teacher to the database."""
        query = """
        INSERT INTO teachers (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING teacher_id
        """
        return self.execute_query(query, (first_name, last_name, email))
    
    def get_teacher(self, teacher_id: int) -> Optional[Dict]:
        """Get a teacher by ID."""
        query = "SELECT * FROM teachers WHERE teacher_id = %s"
        return self.execute_query(query, (teacher_id,), fetch_all=False)
    
    # Student methods
    def add_student(self, first_name: str, last_name: str, email: str, date_of_birth: str = None) -> int:
        """Add a new student to the database."""
        query = """
        INSERT INTO students (first_name, last_name, email, date_of_birth)
        VALUES (%s, %s, %s, %s)
        RETURNING student_id
        """
        return self.execute_query(query, (first_name, last_name, email, date_of_birth))
    
    def get_student(self, student_id: int) -> Optional[Dict]:
        """Get a student by ID."""
        query = "SELECT * FROM students WHERE student_id = %s"
        return self.execute_query(query, (student_id,), fetch_all=False)
    
    # Class methods
    def add_class(self, class_name: str, academic_year: str, semester: str, description: str = None) -> int:
        """Add a new class to the database."""
        query = """
        INSERT INTO classes (class_name, academic_year, semester, description)
        VALUES (%s, %s, %s, %s)
        RETURNING class_id
        """
        return self.execute_query(query, (class_name, academic_year, semester, description))
    
    def get_class(self, class_id: int) -> Optional[Dict]:
        """Get a class by ID."""
        query = "SELECT * FROM classes WHERE class_id = %s"
        return self.execute_query(query, (class_id,), fetch_all=False)
    
    # Subject methods
    def add_subject(self, subject_name: str, subject_code: str = None, description: str = None) -> int:
        """Add a new subject to the database."""
        query = """
        INSERT INTO subjects (subject_name, subject_code, description)
        VALUES (%s, %s, %s)
        RETURNING subject_id
        """
        return self.execute_query(query, (subject_name, subject_code, description))
    
    def get_subject(self, subject_id: int) -> Optional[Dict]:
        """Get a subject by ID."""
        query = "SELECT * FROM subjects WHERE subject_id = %s"
        return self.execute_query(query, (subject_id,), fetch_all=False)
    
    # Enrollment and assignment methods
    def enroll_student_in_class(self, student_id: int, class_id: int, enrollment_date: str = None) -> int:
        """Enroll a student in a class."""
        if not enrollment_date:
            enrollment_date = datetime.now().strftime('%Y-%m-%d')
            
        query = """
        INSERT INTO student_class (student_id, class_id, enrollment_date)
        VALUES (%s, %s, %s)
        RETURNING student_id
        """
        return self.execute_query(query, (student_id, class_id, enrollment_date))
    
    def assign_teacher_to_class_subject(self, teacher_id: int, subject_id: int, class_id: int, 
                                      academic_year: str, semester: str) -> int:
        """Assign a teacher to teach a subject in a specific class, year, and semester."""
        query = """
        INSERT INTO teacher_subject_class (teacher_id, subject_id, class_id, academic_year, semester)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING teacher_id
        """
        return self.execute_query(query, (teacher_id, subject_id, class_id, academic_year, semester))
    
    # Performance methods
    def record_student_performance(self, student_id: int, subject_id: int, class_id: int, 
                                  academic_year: str, semester: str, score: float = None, 
                                  grade: str = None, attendance: int = None) -> int:
        """Record or update a student's performance in a subject."""
        query = """
        INSERT INTO student_subject_performance 
        (student_id, subject_id, class_id, academic_year, semester, score, grade, attendance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(student_id, subject_id, class_id, academic_year, semester)
        DO UPDATE SET 
            score = COALESCE(EXCLUDED.score, student_subject_performance.score),
            grade = COALESCE(EXCLUDED.grade, student_subject_performance.grade),
            attendance = COALESCE(EXCLUDED.attendance, student_subject_performance.attendance),
            updated_at = CURRENT_TIMESTAMP
        RETURNING student_id
        """
        return self.execute_query(query, (student_id, subject_id, class_id, academic_year, 
                                         semester, score, grade, attendance))
    
    # Reporting methods
    def get_student_report(self, student_id: int) -> Dict[str, Any]:
        """Get a comprehensive report for a student."""
        # Get student info
        student = self.get_student(student_id)
        if not student:
            return None
        
        # Get all classes the student is enrolled in
        query = """
        SELECT c.class_id, c.class_name, sc.enrollment_date, sc.status
        FROM student_class sc
        JOIN classes c ON sc.class_id = c.class_id
        WHERE sc.student_id = %s
        """
        classes = self.execute_query(query, (student_id,))
        
        # Get performance in each subject
        query = """
        SELECT s.subject_id, s.subject_name, sp.score, sp.grade, sp.attendance,
               c.class_name, sp.academic_year, sp.semester
        FROM student_subject_performance sp
        JOIN subjects s ON sp.subject_id = s.subject_id
        JOIN classes c ON sp.class_id = c.class_id
        WHERE sp.student_id = %s
        ORDER BY sp.academic_year DESC, sp.semester
        """
        performance = self.execute_query(query, (student_id,))
        
        return {
            'student': dict(student),
            'classes': classes,
            'performance': performance
        }

# Singleton instance
db = Database()

def get_db():
    """Get the database instance."""
    return db

def init_db_with_config(config: Dict[str, str]):
    """Initialize the database with a specific configuration."""
    global db
    db = Database(config)
