from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import csv
import math
import matplotlib
matplotlib.use('Agg')  # Set backend ke Agg sebelum mengimpor pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Ganti dengan secret key yang aman

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_users():
    users = []
    try:
        with open('data/users.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Bersihkan whitespace dari username dan password
                row['username'] = row['username'].strip()
                row['password'] = row['password'].strip()
                users.append(row)
    except Exception as e:
        print(f"Error reading users.csv: {str(e)}")
        # Buat file users.csv jika tidak ada
        with open('data/users.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'password'])
            writer.writeheader()
            writer.writerow({'username': 'admin', 'password': 'admin123'})
            users = [{'username': 'admin', 'password': 'admin123'}]
    return users

def save_users(users):
    with open('data/users.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['username', 'password'])
        writer.writeheader()
        writer.writerows(users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        users = get_users()
        
        print(f"Attempting login with username: {username}")  # Debug
        print(f"Available users: {users}")  # Debug
        
        user = next((user for user in users if user['username'] == username and user['password'] == password), None)
        if user:
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    subject = request.args.get('subject', 'matematika')
    current_subject = subject.lower()
    
    participants = []
    try:
        filename = f"data/{current_subject.capitalize()}.csv"
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            # Skip header rows
            next(reader)
            next(reader)
            next(reader)
            
            for row in reader:
                if len(row) >= 5:
                    participants.append({
                        'Rank': row[0],
                        'Nama Peserta': row[1],
                        'Asal Sekolah': row[2],
                        'Provinsi': row[3],
                        'Nilai': row[4]
                    })
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        flash('Error reading data file')
    
    return render_template('admin_dashboard.html', 
                         participants=participants,
                         current_subject=current_subject,
                         subjects=SUBJECTS)

@app.route('/admin/participant/add', methods=['GET', 'POST'])
@login_required
def add_participant():
    subject = request.args.get('subject', 'matematika')
    current_subject = subject.lower()
    
    if request.method == 'POST':
        new_participant = {
            'Rank': request.form.get('rank'),
            'Nama Peserta': request.form.get('nama'),
            'Asal Sekolah': request.form.get('sekolah'),
            'Provinsi': request.form.get('provinsi'),
            'Nilai': request.form.get('nilai')
        }
        
        participants = []
        try:
            filename = f"data/{current_subject.capitalize()}.csv"
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                # Skip header rows
                next(reader)
                next(reader)
                next(reader)
                
                for row in reader:
                    if len(row) >= 5:
                        participants.append({
                            'Rank': row[0],
                            'Nama Peserta': row[1],
                            'Asal Sekolah': row[2],
                            'Provinsi': row[3],
                            'Nilai': row[4]
                        })
            
            participants.append(new_participant)
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['Column1', 'Column2', 'Column3', 'Column4', 'Column5'])
                writer.writerow(['Hasil TO Pra-KSK Evalator KSN 2022 Bidang ' + current_subject.capitalize(), '', '', '', ''])
                writer.writerow(['Rank', 'Nama Peserta', 'Asal Sekolah', 'Provinsi', 'Nilai'])
                for p in participants:
                    writer.writerow([p['Rank'], p['Nama Peserta'], p['Asal Sekolah'], p['Provinsi'], p['Nilai']])
            
            flash('Participant added successfully')
            return redirect(url_for('admin_dashboard', subject=current_subject))
        except Exception as e:
            print(f"Error writing to CSV file: {str(e)}")
            flash('Error saving data')
    
    return render_template('add_participant.html', current_subject=current_subject)

@app.route('/admin/participant/<int:rank>/edit', methods=['GET', 'POST'])
@login_required
def edit_participant(rank):
    subject = request.args.get('subject', 'matematika')
    current_subject = subject.lower()
    
    participants = []
    try:
        filename = f"data/{current_subject.capitalize()}.csv"
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            # Skip header rows
            next(reader)
            next(reader)
            next(reader)
            
            for row in reader:
                if len(row) >= 5:
                    participants.append({
                        'Rank': row[0],
                        'Nama Peserta': row[1],
                        'Asal Sekolah': row[2],
                        'Provinsi': row[3],
                        'Nilai': row[4]
                    })
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        flash('Error reading data file')
        return redirect(url_for('admin_dashboard', subject=current_subject))
    
    participant = next((p for p in participants if int(p['Rank']) == rank), None)
    if not participant:
        flash('Participant not found')
        return redirect(url_for('admin_dashboard', subject=current_subject))
    
    if request.method == 'POST':
        participant['Nama Peserta'] = request.form.get('nama')
        participant['Asal Sekolah'] = request.form.get('sekolah')
        participant['Provinsi'] = request.form.get('provinsi')
        participant['Nilai'] = request.form.get('nilai')
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(['Column1', 'Column2', 'Column3', 'Column4', 'Column5'])
                writer.writerow(['Hasil TO Pra-KSK Evalator KSN 2022 Bidang ' + current_subject.capitalize(), '', '', '', ''])
                writer.writerow(['Rank', 'Nama Peserta', 'Asal Sekolah', 'Provinsi', 'Nilai'])
                for p in participants:
                    writer.writerow([p['Rank'], p['Nama Peserta'], p['Asal Sekolah'], p['Provinsi'], p['Nilai']])
            
            flash('Participant updated successfully')
            return redirect(url_for('admin_dashboard', subject=current_subject))
        except Exception as e:
            print(f"Error writing to CSV file: {str(e)}")
            flash('Error saving data')
    
    return render_template('edit_participant.html', participant=participant, current_subject=current_subject)

@app.route('/admin/participant/<int:rank>/delete', methods=['POST'])
@login_required
def delete_participant(rank):
    subject = request.args.get('subject', 'matematika')
    current_subject = subject.lower()
    
    participants = []
    try:
        filename = f"data/{current_subject.capitalize()}.csv"
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            # Skip header rows
            next(reader)
            next(reader)
            next(reader)
            
            for row in reader:
                if len(row) >= 5:
                    participants.append({
                        'Rank': row[0],
                        'Nama Peserta': row[1],
                        'Asal Sekolah': row[2],
                        'Provinsi': row[3],
                        'Nilai': row[4]
                    })
        
        # Remove the participant
        participants = [p for p in participants if int(p['Rank']) != rank]
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Column1', 'Column2', 'Column3', 'Column4', 'Column5'])
            writer.writerow(['Hasil TO Pra-KSK Evalator KSN 2022 Bidang ' + current_subject.capitalize(), '', '', '', ''])
            writer.writerow(['Rank', 'Nama Peserta', 'Asal Sekolah', 'Provinsi', 'Nilai'])
            for p in participants:
                writer.writerow([p['Rank'], p['Nama Peserta'], p['Asal Sekolah'], p['Provinsi'], p['Nilai']])
        
        flash('Participant deleted successfully')
    except Exception as e:
        print(f"Error deleting participant: {str(e)}")
        flash('Error deleting participant')
    
    return redirect(url_for('admin_dashboard', subject=current_subject))

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

def read_csv_data(subject):
    """Membaca data dari file CSV sesuai bidang"""
    data = []
    try:
        filename = f"data/{subject.capitalize()}.csv"
        print(f"Reading file: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            # Skip header rows
            next(reader)  # Skip column headers
            next(reader)  # Skip title
            next(reader)  # Skip actual headers
            
            for row in reader:
                row = [cell.strip() for cell in row]
                if len(row) >= 5 and row[0] and row[4]:
                    data.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        raise
    return data

def get_subject_data(data, subject):
    """Mendapatkan data untuk bidang tertentu"""
    subject_data = []
    count = 0
    
    print(f"\nProcessing data for subject: {subject}")
    
    for row in data:
        if count >= 20:
            break
            
        try:
            nilai = row[4].replace(',', '.')
            if nilai.replace('.', '').isdigit():
                score = float(nilai)
                
                subject_data.append({
                    'rank': row[0],
                    'nama': row[1],
                    'sekolah': row[2],
                    'provinsi': row[3],
                    'nilai': score
                })
                count += 1
        except (ValueError, IndexError) as e:
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

def create_histogram(data):
    """Membuat histogram"""
    if not data:
        return None
        
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

def create_box_plot(data):
    """Membuat box plot"""
    if not data:
        return None
        
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

@app.route('/')
def home():
    subject = request.args.get('subject', 'matematika')
    current_subject = subject.lower()
    
    try:
        # Baca data dari file CSV yang sesuai
        print(f"\n=== Starting data processing for subject: {current_subject} ===")
        data = read_csv_data(current_subject)
        print(f"Total rows in CSV: {len(data)}")
        
        # Dapatkan data untuk bidang yang dipilih
        subject_data = get_subject_data(data, current_subject)
        print(f"Found {len(subject_data)} rows for subject {current_subject}")
        
        if not subject_data:
            print("WARNING: No data found for the selected subject!")
        
        # Hitung statistik
        statistics = calculate_statistics(subject_data)
        
        # Buat visualisasi
        stem_leaf_plot = create_stem_leaf_plot(subject_data)
        histogram = create_histogram(subject_data)
        box_plot = create_box_plot(subject_data)
        
        return render_template('home.html',
                             statistics=statistics,
                             current_subject=current_subject,
                             subjects=SUBJECTS,
                             table_data=subject_data,
                             stem_leaf_plot=stem_leaf_plot,
                             histogram=histogram,
                             box_plot=box_plot)
                             
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('home.html',
                             error=str(e),
                             current_subject=current_subject,
                             subjects=SUBJECTS)

@app.route('/compare')
def compare():
    subjects_data = {}
    for subject in SUBJECTS:
        try:
            data = read_csv_data(subject.lower())
            subject_data = get_subject_data(data, subject)
            stats = calculate_statistics(subject_data)
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

if __name__ == '__main__':
    app.run(debug=True) 
