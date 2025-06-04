#!/usr/bin/env python3
"""
Script to drop all tables from the Supabase database.
This is useful for resetting the database to a clean state.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def drop_tables():
    """Drop all tables from the Supabase database"""
    try:
        # Load environment variables
        load_dotenv()
        
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
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True  # Auto-commit each statement
        
        # Create a cursor
        cur = conn.cursor()
        
        # First drop all triggers
        print("Dropping triggers...")
        drop_triggers_sql = """
        DO $$ 
        DECLARE 
            trigger_rec RECORD;
        BEGIN
            FOR trigger_rec IN (
                SELECT trigger_name, event_object_table
                FROM information_schema.triggers
                WHERE trigger_schema = 'public'
            ) LOOP
                EXECUTE 'DROP TRIGGER IF EXISTS ' || trigger_rec.trigger_name || ' ON ' || trigger_rec.event_object_table || ' CASCADE;';
            END LOOP;
        END $$;
        """
        cur.execute(drop_triggers_sql)
        
        # Drop the function
        print("Dropping functions...")
        cur.execute("DROP FUNCTION IF EXISTS update_modified_column() CASCADE;")
        
        # Get a list of all tables
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        # Drop all tables with CASCADE option
        print(f"Found {len(tables)} tables to drop: {', '.join(tables)}")
        
        # Disable foreign key checks
        cur.execute("SET session_replication_role = 'replica';")
        
        # Drop each table
        for table in tables:
            print(f"Dropping table: {table}")
            try:
                cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
            except Exception as e:
                print(f"Error dropping table {table}: {e}")
        
        # Re-enable foreign key checks
        cur.execute("SET session_replication_role = 'origin';")
        
        # Close the connection
        cur.close()
        conn.close()
        
        print("\nAll tables dropped successfully!")
        
    except Exception as e:
        print(f"Error dropping tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("WARNING: This will drop ALL tables from the database!")
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        drop_tables()
    else:
        print("Operation cancelled.")
