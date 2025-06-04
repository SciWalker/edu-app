import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_exec_sql_function():
    """Create a SQL function to execute arbitrary SQL using direct PostgreSQL connection"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database connection string
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("DATABASE_URL environment variable not set")
            return False
        
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
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        
        # Create a cursor
        cur = conn.cursor()
        
        # SQL to create the exec_sql function
        create_function_sql = """
        CREATE OR REPLACE FUNCTION exec_sql(query text)
        RETURNS void AS $$
        BEGIN
            EXECUTE query;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        # Execute the SQL to create the function
        print("Creating exec_sql function...")
        cur.execute(create_function_sql)
        
        # Close the connection
        cur.close()
        conn.close()
        
        print("Created exec_sql function successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating exec_sql function: {e}")
        return False

if __name__ == "__main__":
    create_exec_sql_function()
