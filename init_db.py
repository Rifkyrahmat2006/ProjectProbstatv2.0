import os
from supabase import create_client
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL', 'https://akhgswoguvgkfueibxed.supabase.co'),
    os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFraGdzd29ndXZna2Z1ZWlieGVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwNjY3MzYsImV4cCI6MjA2MDY0MjczNn0.G1gG7HFqMRFKnizAX-QyOWHYBNFeg0-HxUS64BrHBnA')
)

def init_subjects():
    """Initialize subjects table"""
    subjects = [
        {'code': 'matematika', 'name': 'Matematika'},
        {'code': 'fisika', 'name': 'Fisika'},
        {'code': 'kimia', 'name': 'Kimia'},
        {'code': 'biologi', 'name': 'Biologi'},
        {'code': 'informatika', 'name': 'Informatika'},
        {'code': 'ekonomi', 'name': 'Ekonomi'}
    ]
    
    for subject in subjects:
        try:
            supabase.table('subjects').upsert(subject).execute()
            print(f"Added subject: {subject['name']}")
        except Exception as e:
            print(f"Error adding subject {subject['name']}: {str(e)}")

def init_users():
    """Initialize users table with admin user"""
    admin_user = {
        'username': 'admin',
        'password': generate_password_hash('admin123')
    }
    
    try:
        supabase.table('users').upsert(admin_user).execute()
        print("Added admin user")
    except Exception as e:
        print(f"Error adding admin user: {str(e)}")

if __name__ == '__main__':
    print("Initializing database...")
    init_subjects()
    init_users()
    print("Database initialization complete!") 