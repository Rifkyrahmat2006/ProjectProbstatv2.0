# Website Pengolahan Data Hasil Olimpiade

## Struktur Program

```
ProjectProbstatv2/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── foto/
│       └── [foto anggota tim]
│
├── templates/
│   ├── about.html
│   ├── admin_dashboard.html
│   ├── base.html
│   ├── compare.html
│   ├── edit_participant.html
│   ├── edit_subject.html
│   ├── home.html
│   └── login.html
│
├── app.py
└── requirements.txt
```

## Deskripsi Program

Program ini merupakan website pengolahan data hasil olimpiade yang dibangun menggunakan Flask dan Supabase sebagai database. Website ini menampilkan berbagai analisis statistik dan visualisasi data untuk setiap bidang olimpiade.

### Fitur Utama

1. **Manajemen Admin**
   - Login admin
   - Manajemen bidang (tambah, edit, hapus)
   - Import data dari CSV
   - Manajemen peserta (tambah, edit, hapus)

2. **Tabel Data**
   - Menampilkan data peserta (Rank, Nama, Sekolah, Provinsi, Nilai)
   - Pencarian dan filter data berdasarkan nama, sekolah, provinsi, dan bidang
   - Pengurutan berdasarkan nilai

3. **Deskripsi Statistik Data**
   - Data Set (jumlah data dan data terurut)
   - Nilai Minimum dan Maksimum
   - Range
   - Mean atau Rata-rata
   - Median
   - Standar Deviasi
   - Varians
   - Mid Range
   - Modus
   - Quartil (Q1, Q2, Q3)
   - Outliers

4. **Visualisasi Data**
   - Radar Chart (perbandingan antar bidang)
   - Box Plot (sebaran data)
   - Histogram (distribusi frekuensi)
   - Stem and Leaf Plot (pola distribusi)

5. **Penerapan Materi Probstat**
   - Distribusi Frekuensi
   - Statistik Deskriptif
   - Download data statistik dalam format JSON

## Teknologi yang Digunakan

### Backend
- Flask (Web Framework)
- Supabase (Database)
- Perhitungan Statistik Manual (tanpa library eksternal)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Chart.js (Visualisasi Data)
- Font Awesome (Icons)
- Dropzone.js (Upload File)

## Cara Menjalankan Program

1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup Supabase:
   - Buat project di Supabase
   - Salin URL dan API Key ke environment variables
   - Buat tabel `participants` dengan kolom yang sesuai

4. Jalankan aplikasi:
   ```bash
   python app.py
   ```
5. Buka browser dan akses `http://localhost:5000`

## Dependencies

- flask
- python-dotenv
- supabase
- werkzeug

## Fitur Keamanan

- CSRF Protection
- Login Authentication
- Secure Password Storage
- Input Validation

## Fitur Perhitungan Statistik

Semua perhitungan statistik dilakukan secara manual tanpa menggunakan library eksternal:
- Mean (rata-rata)
- Median
- Mode (modus)
- Standard Deviation (simpangan baku)
- Variance (varians)
- Quartiles (Q1, Q2/median, Q3)
- Range dan Mid-range
- Outlier detection
- Frequency distribution

## Tim Pengembang

- Rifky Dwi Rahmat Prakoso (H1D024001)
- Wakhid Nugroho (H1D024003)
- Astria Dina Fitri (H1D024004) 