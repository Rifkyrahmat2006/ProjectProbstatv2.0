from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
import csv
import matplotlib
matplotlib.use('Agg')  # Set backend ke Agg sebelum mengimpor pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
import math
from models import db, User, Participant
from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CSRF protection
csrf = CSRFProtect(app)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            return redirect(url_for('home'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def get_users():
    try:
        response = supabase.table('users').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error reading users: {str(e)}")
        # Create default admin user if table is empty
        try:
            supabase.table('users').insert({
                'username': 'admin',
                'password': 'admin123'
            }).execute()
            return [{'username': 'admin', 'password': 'admin123'}]
        except Exception as e:
            print(f"Error creating default user: {str(e)}")
            return []

def save_users(users):
    try:
        # Delete all existing users
        supabase.table('users').delete().neq('id', 0).execute()
        # Insert new users
        for user in users:
            supabase.table('users').insert(user).execute()
    except Exception as e:
        print(f"Error saving users: {str(e)}")
        raise

# Dictionary untuk mapping kode bidang ke nama lengkap
SUBJECTS = {}

def update_subjects():
    """Update SUBJECTS dictionary from existing data"""
    try:
        response = supabase.table('participants').select('subject').execute()
        if response.data:
            # Get unique subjects
            subjects = set(participant['subject'] for participant in response.data)
            # Update SUBJECTS dictionary
            for subject in subjects:
                if subject not in SUBJECTS:
                    # Convert subject code to proper name
                    name = subject.capitalize()
                    SUBJECTS[subject] = name
    except Exception as e:
        print(f"Error updating subjects: {str(e)}")

# Initialize subjects at startup
update_subjects()

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        # Update subjects before rendering
        update_subjects()
        
        # Get all participants from Supabase
        response = supabase.table('participants').select('*').execute()
        
        if not response.data:
            return render_template('admin_dashboard.html', participants=[], subjects=SUBJECTS)
            
        participants = response.data
        return render_template('admin_dashboard.html', participants=participants, subjects=SUBJECTS)
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/admin/participant/add', methods=['GET', 'POST'])
@login_required
def add_participant():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['nama']
            school = request.form['sekolah']
            province = request.form['provinsi']
            subject = request.form['subject']
            score = float(request.form['nilai'])  # Convert to float instead of int
            
            # Insert into Supabase
            data = {
                'name': name,
                'school': school,
                'province': province,
                'subject': subject,
                'score': score
            }
            response = supabase.table('participants').insert(data).execute()
            
            if response.data:
                flash('Peserta berhasil ditambahkan', 'success')
            else:
                flash('Gagal menambahkan peserta', 'danger')
                
        except Exception as e:
            print(f"Error adding participant: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')
            
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_participant.html', subjects=SUBJECTS)

@app.route('/admin/participant/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_participant(id):
    try:
        response = supabase.table('participants').select('*').eq('id', id).execute()
        participant = response.data[0] if response.data else None
        
        if not participant:
            flash('Participant not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        if request.method == 'POST':
            updated_participant = {
                'name': request.form.get('nama'),
                'school': request.form.get('sekolah'),
                'province': request.form.get('provinsi'),
                'score': float(request.form.get('nilai')),
                'subject': request.form.get('subject')
            }
            
            try:
                supabase.table('participants').update(updated_participant).eq('id', id).execute()
                flash('Participant updated successfully', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                print(f"Error updating participant: {str(e)}")
                flash('Error saving data', 'error')
        
        return render_template('edit_participant.html', participant=participant)
    except Exception as e:
        print(f"Error reading participant: {str(e)}")
        flash('Error reading data', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/participant/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_participant(id):
    try:
        supabase.table('participants').delete().eq('id', id).execute()
        flash('Participant deleted successfully', 'success')
    except Exception as e:
        print(f"Error deleting participant: {str(e)}")
        flash('Error deleting participant', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/participants/delete-selected', methods=['POST'])
@login_required
def delete_selected_participants():
    try:
        selected_ids = request.form.getlist('selected_ids')
        
        if not selected_ids:
            flash('Tidak ada peserta yang dipilih', 'warning')
            return redirect(url_for('admin_dashboard'))
            
        # Delete selected participants
        for participant_id in selected_ids:
            supabase.table('participants').delete().eq('id', participant_id).execute()
            
        flash(f'{len(selected_ids)} peserta berhasil dihapus', 'success')
    except Exception as e:
        print(f"Error deleting participants: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('admin_dashboard'))

def read_csv_data(subject):
    """Membaca data dari Supabase sesuai bidang"""
    try:
        response = supabase.table('participants').select('*').eq('subject', subject.lower()).execute()
        data = response.data
        return data
    except Exception as e:
        print(f"Error reading data: {str(e)}")
        raise

def get_subject_data(data, subject):
    """Mendapatkan data untuk bidang tertentu"""
    subject_data = []
    count = 0
    
    print(f"\nProcessing data for subject: {subject}")
    
    for row in data:
        if count >= 20:
            break
            
        try:
            score = float(row['score'])
            subject_data.append({
                'rank': row['rank'],
                'nama': row['name'],
                'sekolah': row['school'],
                'provinsi': row['province'],
                'nilai': score
            })
            count += 1
        except (ValueError, KeyError) as e:
            print(f"Error processing row: {e}")
            continue
    
    print(f"Total data collected: {len(subject_data)}")
    return subject_data

def calculate_statistics(data):
    """Menghitung statistik dasar"""
    if not data:
        return None
    
    # Ekstrak nilai
    values = [d['nilai'] for d in data]
    n = len(values)
    
    if n == 0:
        return None
    
    # Urutkan nilai
    sorted_values = sorted(values)
    
    # Statistik dasar
    min_val = min(values)
    max_val = max(values)
    mean = sum(values) / n
    
    # Median
    if n % 2 == 0:
        median = (sorted_values[n//2-1] + sorted_values[n//2]) / 2
    else:
        median = sorted_values[n//2]
    
    # Standar deviasi
    variance = sum((x - mean) ** 2 for x in values) / n
    std_dev = math.sqrt(variance)
    
    # Kuartil
    q1_idx = n // 4
    q3_idx = 3 * n // 4
    q1 = sorted_values[q1_idx]
    q3 = sorted_values[q3_idx]
    
    # Modus
    value_counts = {}
    for value in values:
        value_counts[value] = value_counts.get(value, 0) + 1
    mode = max(value_counts.items(), key=lambda x: x[1])[0]
    
    # Distribusi frekuensi
    class_width = (max_val - min_val) / 5  # 5 kelas
    freq_dist = []
    cumulative_freq = 0
    
    for i in range(5):
        class_start = min_val + (i * class_width)
        class_end = class_start + class_width
        frequency = len([x for x in values if class_start <= x < class_end])
        relative_freq = (frequency / n) * 100
        cumulative_freq += frequency
        
        freq_dist.append({
            'class_range': f"{class_start:.1f}-{class_end:.1f}",
            'frequency': frequency,
            'relative_frequency': relative_freq,
            'cumulative_frequency': cumulative_freq
        })
    
    return {
        'n': n,
        'min': min_val,
        'max': max_val,
        'mean': mean,
        'median': median,
        'std_dev': std_dev,
        'q1': q1,
        'q3': q3,
        'mode': mode,
        'frequency_distribution': freq_dist,
        'sorted_data': sorted_values
    }

def create_stem_leaf_plot(data):
    """Membuat stem and leaf plot"""
    if not data:
        return None
        
    try:
        plt.clf()  # Clear figure
        plt.figure(figsize=(10, 6))
        values = [d['nilai'] for d in data]
        
        # Pisahkan stem dan leaf
        stems = []
        leaves = []
        for value in sorted(values):
            stem = int(value // 10)
            leaf = int(value % 10)
            stems.append(stem)
            leaves.append(leaf)
        
        # Buat plot
        plt.stem(stems, leaves)
        plt.title('Stem and Leaf Plot')
        plt.xlabel('Stem')
        plt.ylabel('Leaf')
        
        # Simpan plot ke buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"Error creating stem and leaf plot: {str(e)}")
        return None

def create_histogram(data):
    """Membuat histogram"""
    if not data:
        return None
        
    try:
        plt.clf()  # Clear figure
        plt.figure(figsize=(10, 6))
        values = [d['nilai'] for d in data]
        
        # Buat histogram
        sns.histplot(values, bins=5)
        plt.title('Histogram')
        plt.xlabel('Nilai')
        plt.ylabel('Frekuensi')
        
        # Simpan plot ke buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"Error creating histogram: {str(e)}")
        return None

def create_box_plot(data):
    """Membuat box plot"""
    if not data:
        return None
        
    try:
        plt.clf()  # Clear figure
        plt.figure(figsize=(10, 6))
        values = [d['nilai'] for d in data]
        
        # Buat box plot
        sns.boxplot(y=values)
        plt.title('Box Plot')
        plt.ylabel('Nilai')
        
        # Simpan plot ke buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"Error creating box plot: {str(e)}")
        return None

@app.route('/')
def home():
    try:
        # Get current subject from query parameter, default to 'all'
        current_subject = request.args.get('subject', 'all')
        
        # Get all participants from Supabase
        if current_subject == 'all':
            response = supabase.table('participants').select('*').order('score', desc=True).execute()
        else:
            response = supabase.table('participants').select('*').eq('subject', current_subject).order('score', desc=True).execute()
        
        if not response.data:
            return render_template('home.html', participants=[], subjects=SUBJECTS, current_subject=current_subject)
            
        participants = response.data
        return render_template('home.html', participants=participants, subjects=SUBJECTS, current_subject=current_subject)
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return render_template('home.html', participants=[], subjects=SUBJECTS, current_subject='all')

@app.route('/compare')
def compare():
    subjects_data = {}
    for subject in SUBJECTS:
        try:
            # Get data directly from Supabase
            response = supabase.table('participants').select('*').eq('subject', subject.lower()).execute()
            data = response.data
            
            # Calculate statistics
            stats = calculate_statistics(data)
            subjects_data[subject] = stats
        except Exception as e:
            print(f"Error processing {subject}: {str(e)}")
            continue
    
    # Prepare data for radar chart
    labels = ['Mean', 'Median', 'Std Dev', 'Q1', 'Q3']
    datasets = []
    
    colors = [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(199, 199, 199, 0.2)',
        'rgba(83, 102, 255, 0.2)',
        'rgba(40, 159, 64, 0.2)'
    ]
    
    borders = [color.replace('0.2', '1') for color in colors]
    
    for i, (subject, stats) in enumerate(subjects_data.items()):
        if stats:  # Only add if stats exist
            datasets.append({
                'label': SUBJECTS[subject],
                'data': [stats['mean'], stats['median'], stats['std_dev'], stats['q1'], stats['q3']],
                'backgroundColor': colors[i],
                'borderColor': borders[i],
                'borderWidth': 1
            })
    
    return render_template('compare.html', 
                         subjects_data=subjects_data,
                         subjects=SUBJECTS,
                         radar_labels=labels,
                         radar_datasets=datasets)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        try:
            subject_key = request.form['subject_key'].lower()
            subject_name = request.form['subject_name']
            
            # Update SUBJECTS dictionary
            SUBJECTS[subject_key] = subject_name
            
            flash('Bidang berhasil ditambahkan', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_subject.html')

@app.route('/admin/import_csv', methods=['POST'])
@login_required
def import_csv():
    try:
        if 'csv_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Tidak ada file yang dipilih',
                'redirect': url_for('admin_dashboard')
            })
            
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Tidak ada file yang dipilih',
                'redirect': url_for('admin_dashboard')
            })
            
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': 'File harus berformat CSV',
                'redirect': url_for('admin_dashboard')
            })
            
        # Extract subject from filename (format: subject_name.csv)
        subject = file.filename.split('.')[0].lower()
        
        # Read CSV file
        import csv
        from io import StringIO
        
        # Convert file to string
        content = file.read().decode('utf-8')
        csv_data = StringIO(content)
        reader = csv.reader(csv_data, delimiter=';')
        
        # Skip header rows if they exist
        try:
            next(reader)  # Skip first header
            next(reader)  # Skip second header
            next(reader)  # Skip third header
        except StopIteration:
            csv_data.seek(0)
            reader = csv.reader(csv_data, delimiter=';')
        
        # First pass: collect all scores to calculate ranks
        rows_with_scores = []
        for row in reader:
            if len(row) >= 5:  # Make sure row has enough columns
                try:
                    score = float(row[4].replace(',', '.'))
                    rows_with_scores.append({
                        'name': row[1],
                        'school': row[2],
                        'province': row[3],
                        'score': score,
                        'subject': subject
                    })
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    continue
        
        # Sort by score in descending order
        rows_with_scores.sort(key=lambda x: x['score'], reverse=True)
        
        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        # Check for duplicates and insert into Supabase
        for rank, row_data in enumerate(rows_with_scores, 1):
            try:
                # Check for duplicates
                response = supabase.table('participants').select('*').eq('name', row_data['name']).eq('subject', subject).execute()
                
                if response.data:
                    duplicate_count += 1
                    continue
                
                # Add rank to the data
                row_data['rank'] = rank
                
                # Insert into Supabase
                supabase.table('participants').insert(row_data).execute()
                success_count += 1
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                error_count += 1
                continue
        
        # Update subjects dictionary
        update_subjects()
        
        message = f'Berhasil mengimpor {success_count} data ke bidang {subject}. {duplicate_count} data duplikat ditemukan. {error_count} data gagal diimpor.' if success_count > 0 else 'Tidak ada data yang berhasil diimpor'
        
        return jsonify({
            'success': True,
            'message': message,
            'redirect': url_for('admin_dashboard')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'redirect': url_for('admin_dashboard')
        })

@app.route('/admin/delete_subject/<subject_key>', methods=['POST'])
@login_required
def delete_subject(subject_key):
    try:
        if subject_key in SUBJECTS:
            # Delete subject from dictionary
            del SUBJECTS[subject_key]
            
            # Delete all participants with this subject
            supabase.table('participants').delete().eq('subject', subject_key).execute()
            
            flash('Bidang berhasil dihapus', 'success')
        else:
            flash('Bidang tidak ditemukan', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True) 
