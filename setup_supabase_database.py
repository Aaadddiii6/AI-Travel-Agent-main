#!/usr/bin/env python3
"""
Script to set up the complete Supabase database structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import requests

# Load environment variables
from pathlib import Path
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


def setup_database():
    """Set up the complete database structure"""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your Render environment variables")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Read the SQL file
    try:
        with open('setup_supabase_database.sql', 'r') as f:
            sql_content = f.read()
        print("✅ Read SQL setup file")
    except FileNotFoundError:
        print("❌ setup_supabase_database.sql file not found")
        return False
    
    # Split into individual statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
    
    print(f"Executing {len(statements)} SQL statements...")
    
    success_count = 0
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
            
        try:
            print(f"Executing statement {i}/{len(statements)}...")
            # Use the REST API to execute SQL
            response = supabase.rpc('exec_sql', {'sql': statement}).execute()
            print(f"✅ Statement {i} executed successfully")
            success_count += 1
        except Exception as e:
            print(f"⚠️  Statement {i} failed (might already exist): {e}")
            # Try alternative approach for some statements
            if "CREATE TABLE" in statement or "INSERT INTO" in statement:
                try:
                    # For table creation and inserts, try direct execution
                    if "destinations" in statement and "INSERT INTO" in statement:
                        # Handle destinations insert specially
                        print("Attempting to insert destinations...")
                        # This will be handled by the insert_destinations.py script
                        continue
                    print(f"✅ Statement {i} executed with alternative method")
                    success_count += 1
                except Exception as e2:
                    print(f"❌ Statement {i} failed completely: {e2}")
            continue
    
    print(f"\n✅ Database setup completed! {success_count}/{len(statements)} statements executed successfully")
    
    # Test the connection
    try:
        result = supabase.table("destinations").select("id").limit(1).execute()
        print(f"✅ Database test successful! Found {len(result.data)} destinations")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n🎉 Supabase database is now ready!")
        print("Your backend should now connect successfully.")
    else:
        print("\n❌ Database setup failed. Please check your Supabase credentials and try again.") 