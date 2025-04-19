import csv
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Dictionary untuk mapping kode bidang ke nama lengkap
SUBJECTS = {
    'matematika': 'Matematika',
    'fisika': 'Fisika',
    'kimia': 'Kimia',
    'biologi': 'Biologi',
    'informatika': 'Informatika',
    'astronomi': 'Astronomi',
    'ekonomi': 'Ekonomi',
    'kebumian': 'Kebumian',
    'geografi': 'Geografi'
}

def migrate_data():
    # Migrate users
    try:
        with open('data/users.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                supabase.table('users').insert({
                    'username': row['username'].strip(),
                    'password': row['password'].strip()
                }).execute()
        print("Users migrated successfully")
    except Exception as e:
        print(f"Error migrating users: {str(e)}")

    # Migrate participants
    for subject in SUBJECTS:
        try:
            filename = f"data/{subject.capitalize()}.csv"
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                # Skip header rows
                next(reader)
                next(reader)
                next(reader)
                
                for row in reader:
                    if len(row) >= 5:
                        try:
                            score = float(row[4].replace(',', '.'))
                            supabase.table('participants').insert({
                                'rank': int(row[0]),
                                'name': row[1],
                                'school': row[2],
                                'province': row[3],
                                'score': score,
                                'subject': subject.lower()
                            }).execute()
                        except (ValueError, IndexError) as e:
                            print(f"Error processing row for {subject}: {e}")
                            continue
            print(f"{subject.capitalize()} data migrated successfully")
        except Exception as e:
            print(f"Error migrating {subject} data: {str(e)}")

if __name__ == "__main__":
    migrate_data() 