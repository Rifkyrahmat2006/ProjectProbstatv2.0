# Website Pengolahan Data Hasil Tryout SNBT

## Deskripsi Program

Program ini merupakan website pengolahan data hasil tryout SNBT yang dibangun menggunakan Flask dan Supabase sebagai database. Website ini menampilkan berbagai analisis statistik dan visualisasi data untuk setiap bidang ujian.

### Fitur Utama

1. **Admin Dashboard**
   - Manajemen data peserta (tambah, edit, hapus)
   - Manajemen bidang (tambah, edit, hapus)
   - Import data dari file CSV
   - Pencarian dan filter data peserta

2. **Visualisasi Data**
   - Radar Chart
   - Box Plot
   - Histogram
   - Stem and Leaf Plot
   - Download statistik dalam format JSON

3. **Analisis Statistik**
   - Ukuran data (n)
   - Data terurut
   - Nilai minimum dan maksimum
   - Mean (rata-rata)
   - Median
   - Standar deviasi
   - Quartil (Q1, Q2, Q3)
   - Modus
   - Distribusi frekuensi

4. **Fitur Keamanan**
   - Login admin
   - CSRF protection
   - Validasi input

## Teknologi yang Digunakan

### Backend
- Flask (Web Framework)
- Supabase (Database)
- NumPy (Perhitungan Statistik)
- Chart.js (Visualisasi Data)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Font Awesome (Icons)
- Dropzone.js (Upload File)

### Database
- Supabase (PostgreSQL)

## Cara Menjalankan Program

### Lokal
1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup environment variables:
   - `SUPABASE_URL`: URL Supabase Anda
   - `SUPABASE_KEY`: API Key Supabase Anda
   - `SECRET_KEY`: Secret key untuk Flask session

4. Jalankan aplikasi:
   ```bash
   python app.py
   ```
5. Buka browser dan akses `http://localhost:5000`

### Deployment di Vercel
1. Fork repository ini ke akun GitHub Anda
2. Buat akun di Vercel (vercel.com)
3. Import repository dari GitHub ke Vercel
4. Setup environment variables di Vercel:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SECRET_KEY`
5. Deploy aplikasi

## Struktur Database

### Tabel `participants`
- id (integer, primary key)
- name (text)
- school (text)
- province (text)
- subject (text)
- score (float)
- rank (integer)

## Fitur yang Akan Datang
- Export data ke Excel
- Grafik perbandingan antar provinsi
- Analisis trend nilai
- Dashboard statistik real-time

## Tim Pengembang
- Rifky Dwi Rahmat Prakoso (H1D024001)
- Wakhid Nugroho (H1D024003)
- Astria Dina Fitri (H1D024004)

## Lisensi
MIT License 