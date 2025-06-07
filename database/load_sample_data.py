import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_sample_data():
    """Load sample data into the database"""
    conn = None
    cur = None
    try:
        # Load environment variables
        load_dotenv()
        
        # Read the sample data file
        sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data.sql')
        with open(sample_data_path, 'r') as f:
            sample_data_sql = f.read()
        
        # Get database connection string
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("DATABASE_URL environment variable not set")
            sys.exit(1)
        
        # Parse the connection string
        parsed_url = urlparse(db_url)
        
        # Extract connection parameters
        dbname = parsed_url.path[1:]  # Remove leading slash
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        
        # Connect to the database
        print(f"Connecting to database at {host}:{port}...")
        print(f"Database: {dbname}")
        
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        except Exception as e:
            print(f"Connection error: {e}")
            # Try with sslmode=require
            print("Trying with sslmode=require...")
            try:
                conn = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    sslmode='require'
                )
            except Exception as e:
                print(f"Connection error with sslmode=require: {e}")
                raise
        
        # Turn off autocommit to use transaction
        conn.autocommit = False
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check if tables exist and have data
        try:
            cur.execute("SELECT COUNT(*) FROM classes")
            count = cur.fetchone()[0]
            print(f"Current number of records in classes table: {count}")
            
            if count > 0:
                print("Tables already contain data. Do you want to proceed? (y/n)")
                response = input().strip().lower()
                if response != 'y':
                    print("Operation cancelled by user.")
                    return
        except Exception as e:
            print(f"Error checking tables: {e}")
            print("Tables may not exist yet. Make sure to run init_db.py first.")
            return
        
        # Execute entire SQL script in a single command
        try:
            cur.execute(sample_data_sql)
            conn.commit()
            print("\nSample data inserted successfully!")
        except Exception as e:
            conn.rollback()
            print(f"Error executing sample data SQL: {e}")
            return
        
        # Verify data was inserted
        tables = ['teachers', 'students', 'classes', 'subjects', 
                 'student_class', 'teacher_subject_class', 'student_subject_performance']
        print("\nVerifying data insertion:")
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"Table {table}: {count} records")
            except Exception as e:
                print(f"Error checking table {table}: {e}")
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        # Close the connection
        if conn:
            if cur:
                cur.close()
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    print("Loading sample data into database...")
    load_sample_data()
