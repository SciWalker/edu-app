import os
import sys
import re
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_tables():
    """Create all necessary tables in the Supabase database using direct PostgreSQL connection"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
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
        print(f"User: {user}")
        # Don't print the actual password for security reasons
        print(f"Password length: {len(password) if password else 0}")
        
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
        conn.autocommit = True  # Auto-commit each statement
        
        # Create a cursor
        cur = conn.cursor()
        
        # Read the function definition separately
        function_pattern = r'CREATE OR REPLACE FUNCTION update_modified_column\(\)[\s\S]*?\$\$ LANGUAGE plpgsql;'
        function_match = re.search(function_pattern, schema_sql)
        
        # Execute the function definition as a single statement if found
        if function_match:
            function_sql = function_match.group(0)
            try:
                cur.execute(function_sql)
                print("Created update_modified_column function successfully")
            except Exception as e:
                print(f"Error creating function: {e}")
        
        # Remove the function definition from the schema SQL
        if function_match:
            schema_sql = schema_sql.replace(function_match.group(0), '')
        
        # Split the remaining SQL file into individual statements
        # This regex splits on semicolons but ignores those within quotes
        statements = re.split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', schema_sql)
        
        # Execute each statement
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:  # Skip empty statements
                try:
                    # Execute the SQL statement directly
                    cur.execute(stmt)
                    print(f"Executed: {stmt[:50]}...")
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {stmt}")
                    continue
        
        # Close the connection
        cur.close()
        conn.close()
        
        print("\nDatabase tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Initializing database tables...")
    create_tables()
