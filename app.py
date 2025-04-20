from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
import csv
import io
import base64
import numpy as np
import math
from models import db, User, Participant
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL', 'https://akhgswoguvgkfueibxed.supabase.co'),
    os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFraGdzd29ndXZna2Z1ZWlieGVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwNjY3MzYsImV4cCI6MjA2MDY0MjczNn0.G1gG7HFqMRFKnizAX-QyOWHYBNFeg0-HxUS64BrHBnA')
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '3da440d6050e223aa0d3883def14c34b314faac792eda4dd12ed27020084a768')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Initialize CSRF protection
csrf = CSRFProtect(app)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Custom login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Check user credentials in Supabase
            response = supabase.table('users').select('*').eq('username', username).execute()
            
            if response.data and check_password_hash(response.data[0]['password'], password):
                session['user_id'] = response.data[0]['id']
                session['username'] = username
                session.permanent = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('Error during login', 'error')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
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

# Dictionary of subjects (will be managed in Supabase)
SUBJECTS = {}

def update_subjects():
    """Update subjects from Supabase"""
    try:
        response = supabase.table('subjects').select('*').execute()
        if response.data:
            SUBJECTS.clear()
            for subject in response.data:
                SUBJECTS[subject['code']] = subject['name']
    except Exception as e:
        print(f"Error updating subjects: {str(e)}")

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        update_subjects()
        response = supabase.table('participants').select('*').execute()
        participants = response.data if response.data else []
        participants.sort(key=lambda x: (-float(x['score']), x['name']))
        
        return render_template('admin_dashboard.html', 
                             participants=participants,
                             subjects=SUBJECTS)
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
            score = float(request.form['nilai'])  # Convert to float
            
            # Get current participants for the subject to calculate rank
            response = supabase.table('participants').select('*').eq('subject', subject).order('score', desc=True).execute()
            current_participants = response.data
            
            # Calculate rank based on score
            rank = 1
            for participant in current_participants:
                if float(participant['score']) > score:
                    rank += 1
            
            # Insert into Supabase
            data = {
                'name': name,
                'school': school,
                'province': province,
                'subject': subject,
                'score': score,
                'rank': rank
            }
            response = supabase.table('participants').insert(data).execute()
            
            if response.data:
                # Update ranks for other participants
                for participant in current_participants:
                    if float(participant['score']) <= score:
                        supabase.table('participants').update({'rank': participant['rank'] + 1}).eq('id', participant['id']).execute()
                
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
        
        return render_template('edit_participant.html', participant=participant, subjects=SUBJECTS)
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
    """Get data for specific subject"""
    try:
        subject_data = []
        for row in data:
            if isinstance(row, dict):
                subject_data.append({
                    'name': row.get('name', ''),
                    'school': row.get('school', ''),
                    'province': row.get('province', ''),
                    'score': float(row.get('score', 0))
                })
        return subject_data
    except Exception as e:
        print(f"Error in get_subject_data: {str(e)}")
        return []

def calculate_statistics(participants):
    """Calculate statistics for the given participants"""
    try:
        if not participants:
            return {
                'n': 0,
                'sorted_data': [],
                'min': 0,
                'max': 0,
                'mean': 0,
                'median': 0,
                'std_dev': 0,
                'q1': 0,
                'q3': 0,
                'mode': 0,
                'frequency_distribution': []
            }
        
        # Extract and sort scores
        scores = []
        for p in participants:
            try:
                score = float(p['score'])
                if not math.isnan(score) and not math.isinf(score):
                    scores.append(score)
            except (ValueError, TypeError, KeyError):
                continue
        
        if not scores:
            return {
                'n': 0,
                'sorted_data': [],
                'min': 0,
                'max': 0,
                'mean': 0,
                'median': 0,
                'std_dev': 0,
                'q1': 0,
                'q3': 0,
                'mode': 0,
                'frequency_distribution': []
            }
            
        scores.sort()
        
        # Basic statistics
        n = len(scores)
        min_score = min(scores)
        max_score = max(scores)
        mean = sum(scores) / n
        
        # Median calculation
        if n % 2 == 0:
            median = (scores[n//2 - 1] + scores[n//2]) / 2
        else:
            median = scores[n//2]
        
        # Quartiles calculation
        def get_quartile(sorted_data, q):
            n = len(sorted_data)
            pos = (n - 1) * q
            floor = math.floor(pos)
            ceil = math.ceil(pos)
            
            if floor == ceil:
                return sorted_data[floor]
            
            d0 = sorted_data[floor] * (ceil - pos)
            d1 = sorted_data[ceil] * (pos - floor)
            return d0 + d1
        
        q1 = get_quartile(scores, 0.25)
        q3 = get_quartile(scores, 0.75)
        
        # Standard deviation calculation
        squared_diff_sum = sum((x - mean) ** 2 for x in scores)
        std_dev = math.sqrt(squared_diff_sum / (n - 1) if n > 1 else 0)
        
        # Mode calculation
        score_counts = {}
        for score in scores:
            score_counts[score] = score_counts.get(score, 0) + 1
        mode = max(score_counts.items(), key=lambda x: x[1])[0]
        
        # Frequency distribution
        bin_size = (max_score - min_score) / 5 if max_score != min_score else 1
        frequency_distribution = []
        cumulative_frequency = 0
        
        for i in range(5):
            start = min_score + (i * bin_size)
            end = start + bin_size
            frequency = len([s for s in scores if start <= s < end])
            cumulative_frequency += frequency
            relative_frequency = (frequency / n) * 100 if n > 0 else 0
            
            frequency_distribution.append({
                'class_range': f"{start:.1f}-{end:.1f}",
                'frequency': frequency,
                'relative_frequency': relative_frequency,
                'cumulative_frequency': cumulative_frequency
            })
        
        # Calculate variance
        variance = squared_diff_sum / (n - 1) if n > 1 else 0
        
        # Calculate mid-range
        mid_range = (max_score + min_score) / 2
        
        # Calculate range
        range_value = max_score - min_score
        
        # Calculate outliers
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outliers = [x for x in scores if x < lower_bound or x > upper_bound]
        
        return {
            'n': n,
            'sorted_data': scores,
            'min': min_score,
            'max': max_score,
            'range': range_value,
            'mean': mean,
            'median': median,
            'std_dev': std_dev,
            'variance': variance,
            'q1': q1,
            'q3': q3,
            'mode': mode,
            'mid_range': mid_range,
            'iqr': iqr,
            'outliers': outliers,
            'frequency_distribution': frequency_distribution
        }
    except Exception as e:
        print(f"Error in calculate_statistics: {str(e)}")
        return {
            'n': 0,
            'sorted_data': [],
            'min': 0,
            'max': 0,
            'mean': 0,
            'median': 0,
            'std_dev': 0,
            'q1': 0,
            'q3': 0,
            'mode': 0,
            'frequency_distribution': []
        }

@app.route('/')
def home():
    try:
        # Get subject from query parameter, validate it
        subject = request.args.get('subject', 'all')
        if subject != 'all' and subject not in SUBJECTS:
            flash('Invalid subject selected', 'warning')
            subject = 'all'
        
        # Update subjects before rendering
        try:
            update_subjects()
        except Exception as e:
            app.logger.error(f"Failed to update subjects: {str(e)}")
            flash('Failed to update subjects list', 'warning')
        
        # Get all participants from Supabase
        try:
            response = supabase.table('participants').select('*').order('score', desc=True).execute()
            participants = response.data if response.data else []
        except Exception as e:
            app.logger.error(f"Failed to fetch participants: {str(e)}")
            flash('Failed to fetch participants data', 'danger')
            return render_template('home.html',
                                participants=[],
                                statistics={},
                                subjects=SUBJECTS,
                                current_subject=subject)
        
        # Sort participants by score in descending order
        try:
            participants.sort(key=lambda x: float(x.get('score', 0)), reverse=True)
        except ValueError as e:
            app.logger.error(f"Invalid score value found: {str(e)}")
            flash('Some participant scores are invalid', 'warning')
            participants.sort(key=lambda x: float(x.get('score', 0) or 0), reverse=True)
        
        if subject != 'all':
            # Filter participants by subject
            participants = [p for p in participants if p.get('subject') == subject]
            # Update ranks for filtered participants
            for i, p in enumerate(participants, 1):
                p['rank'] = i
        else:
            # For 'all', recalculate ranks based on overall scores
            current_rank = 1
            current_score = None
            same_rank_count = 0
            
            for p in participants:
                try:
                    score = float(p.get('score', 0))
                    if score != current_score:
                        current_rank += same_rank_count
                        same_rank_count = 1
                        current_score = score
                    else:
                        same_rank_count += 1
                    p['rank'] = current_rank
                except (ValueError, TypeError) as e:
                    app.logger.error(f"Error calculating rank for participant {p.get('id')}: {str(e)}")
                    p['rank'] = current_rank
                    current_rank += 1
        
        # Calculate statistics
        try:
            statistics = calculate_statistics(participants)
        except Exception as e:
            app.logger.error(f"Failed to calculate statistics: {str(e)}")
            flash('Failed to calculate statistics', 'warning')
            statistics = {}
        
        return render_template('home.html',
                             participants=participants,
                             statistics=statistics,
                             subjects=SUBJECTS,
                             current_subject=subject)
    except Exception as e:
        app.logger.error(f"Unexpected error in home route: {str(e)}")
        flash('An unexpected error occurred', 'danger')
        return render_template('home.html',
                             participants=[],
                             statistics={},
                             subjects=SUBJECTS,
                             current_subject='all')

@app.route('/compare')
def compare():
    try:
        # Update subjects before rendering
        try:
            update_subjects()
        except Exception as e:
            app.logger.error(f"Failed to update subjects: {str(e)}")
            flash('Failed to update subjects list', 'warning')
        
        # Get all participants from Supabase
        try:
            response = supabase.table('participants').select('*').execute()
            all_participants = response.data if response.data else []
        except Exception as e:
            app.logger.error(f"Failed to fetch participants: {str(e)}")
            flash('Failed to fetch participants data', 'danger')
            return render_template('compare.html', 
                                subjects_data={},
                                subjects=SUBJECTS)
        
        # Group participants by subject
        subjects_data = {}
        for subject in SUBJECTS:
            try:
                # Filter participants by subject
                participants = [p for p in all_participants if p.get('subject') == subject]
                
                if participants:
                    # Calculate statistics for the subject
                    stats = calculate_statistics(participants)
                    if stats:
                        subjects_data[subject] = {
                            'name': SUBJECTS.get(subject, 'Unknown'),
                            'stats': stats,
                            'participants': participants
                        }
            except Exception as e:
                app.logger.error(f"Error processing subject {subject}: {str(e)}")
                continue
        
        if not subjects_data:
            flash('No data available for comparison', 'info')
        
        return render_template('compare.html', 
                             subjects_data=subjects_data,
                             subjects=SUBJECTS)
    except Exception as e:
        app.logger.error(f"Unexpected error in compare route: {str(e)}")
        flash('An unexpected error occurred', 'danger')
        return render_template('compare.html', 
                             subjects_data={},
                             subjects=SUBJECTS)

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
        try:
            subject = file.filename.split('.')[0].lower()
            if subject not in SUBJECTS:
                return jsonify({
                    'success': False,
                    'message': f'Subject "{subject}" not found in registered subjects',
                    'redirect': url_for('admin_dashboard')
                })
        except Exception as e:
            app.logger.error(f"Error extracting subject from filename: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid filename format',
                'redirect': url_for('admin_dashboard')
            })
            
        # Read CSV file
        try:
            import csv
            from io import StringIO
            
            # Convert file to string and detect encoding
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    file.seek(0)
                    content = file.read().decode('latin-1')
                except Exception as e:
                    app.logger.error(f"Failed to decode file: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': 'File encoding not supported',
                        'redirect': url_for('admin_dashboard')
                    })
            
            csv_data = StringIO(content)
            reader = csv.reader(csv_data, delimiter=';')
            
            # Skip header rows if they exist
            try:
                next(reader)  # Skip first header
                next(reader)  # Skip second header
                next(reader)  # Skip third header
            except StopIteration:
                return jsonify({
                    'success': False,
                    'message': 'File is empty or has invalid format',
                    'redirect': url_for('admin_dashboard')
                })
            
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

@app.route('/api/statistics')
def get_statistics():
    subjects_data = {}
    for subject in SUBJECTS:
        try:
            # Get data directly from Supabase
            response = supabase.table('participants').select('*').eq('subject', subject.lower()).execute()
            data = response.data
            
            if not data:
                continue
                
            # Convert data to required format
            formatted_data = []
            for item in data:
                try:
                    score = float(item.get('score', 0))
                    formatted_data.append({
                        'nilai': score,
                        'nama': item.get('name', ''),
                        'sekolah': item.get('school', ''),
                        'provinsi': item.get('province', '')
                    })
                except (ValueError, TypeError) as e:
                    print(f"Error processing item: {str(e)}")
                    continue
            
            if not formatted_data:
                continue
                
            # Calculate statistics
            stats = calculate_statistics(formatted_data)
            if stats:
                subjects_data[subject] = {
                    'name': SUBJECTS[subject],
                    'stats': stats
                }
        except Exception as e:
            print(f"Error processing {subject}: {str(e)}")
            continue
    
    return jsonify(subjects_data)

@app.route('/edit_subject/<subject_key>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_key):
    if request.method == 'POST':
        new_name = request.form.get('subject_name')
        if new_name and subject_key in SUBJECTS:
            # Update subject in SUBJECTS dictionary
            old_name = SUBJECTS[subject_key]
            SUBJECTS[subject_key] = new_name
            
            # Update subject in participants table
            try:
                # Get all participants with this subject
                response = supabase.table('participants').select('*').eq('subject', subject_key).execute()
                if response.data:
                    # Update each participant's subject
                    supabase.table('participants').update({
                        'subject': subject_key  # Ensure subject code is consistent
                    }).eq('subject', subject_key).execute()
            except Exception as e:
                print(f"Error updating participants: {str(e)}")
                flash('Terjadi kesalahan saat memperbarui data peserta', 'error')
                return redirect(url_for('admin_dashboard'))
            
            flash('Bidang berhasil diperbarui!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    # Get current subject data
    if subject_key not in SUBJECTS:
        flash('Bidang tidak ditemukan!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_subject.html', subject={'code': subject_key, 'name': SUBJECTS[subject_key]})

if __name__ == '__main__':
    app.run()

# Add WSGI handler for serverless
app = app
