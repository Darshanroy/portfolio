import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Testing connection to: {url}")

try:
    if not url or not key:
        print("ERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env")
    else:
        supabase = create_client(url, key)
        # Try a simple select
        res = supabase.table('projects').select('count', count='exact').execute()
        print(f"SUCCESS! Connected to Supabase.")
        print(f"Found {res.count} projects in the database.")
except Exception as e:
    print(f"CONNECTION FAILED: {str(e)}")
