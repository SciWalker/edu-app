import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

def get_supabase() -> Client:
    """
    Initialize and return a Supabase client.
    
    Returns:
        Client: An instance of the Supabase client
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase URL and key must be set in the .env file. "
            "Please copy .env.example to .env and fill in your credentials."
        )
    
    return create_client(supabase_url, supabase_key)

# Example usage:
# supabase = get_supabase()
# result = supabase.table('your_table').select('*').execute()
# print(result)
