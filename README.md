# Website Pengolahan Data Hasil Tryout SNBT

## Struktur Program

```
Program1/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── base.html
│   └── home.html
│
├── data/
│   ├── Matematika.csv
│   ├── Fisika.csv
│   ├── Kimia.csv
│   ├── Biologi.csv
│   ├── Informatika.csv
│   ├── Astronomi.csv
│   ├── Ekonomi.csv
│   ├── Kebumian.csv
│   └── Geografi.csv
│
├── app.py
├── requirements.txt
└── vercel.json
```

## Deskripsi Program

Program ini merupakan website pengolahan data hasil tryout SNBT yang dibangun menggunakan Flask. Website ini menampilkan berbagai analisis statistik dan visualisasi data untuk setiap bidang ujian.

### Fitur Utama

1. **Pilih Bidang**
   - Pemilihan bidang ujian (Matematika, Fisika, Kimia, dll.)
   - Tampilan data sesuai bidang yang dipilih

2. **Tabel Data**
   - Menampilkan data peserta (Rank, Nama, Sekolah, Provinsi, Nilai)
   - Data dibatasi 20 peserta per bidang

3. **Deskripsi Statistik Data**
   - Data Set (jumlah data dan data terurut)
   - Nilai Minimum dan Maksimum
   - Range
   - Mean atau Rata-rata
   - Median
   - Standar Deviasi
   - Varians
   - Mid Range
   - Quartil (Q1, Q2, Q3)
   - Interquartil Range (IQR)
   - Outliers

4. **Data Dalam Bentuk Diagram**
   - Diagram Stem and Leaf
   - Histogram
   - Box Plot

5. **Penerapan Materi Probstat**
   - Distribusi Frekuensi
   - Statistik Deskriptif (Skewness, Kurtosis, Modus)

6. **Kasus Penerapan Materi**
   - Diketahui: informasi dasar tentang data
   - Pertanyaan: soal-soal probabilitas
   - Jawaban: solusi menggunakan teori probabilitas

## Teknologi yang Digunakan

### Library Python
- Flask (Web Framework)
- Matplotlib (Visualisasi Data)
- Seaborn (Visualisasi Data)

### Library Bawaan Python
- csv (Pembacaan file CSV)
- os (Operasi file)
- math (Perhitungan statistik)
- io (BytesIO untuk gambar)
- base64 (Encoding gambar)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Cara Menjalankan Program

### Lokal
1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
4. Buka browser dan akses `http://localhost:5000`

### Deployment di Vercel
1. Push kode ke repository Git
2. Hubungkan repository ke Vercel
3. Vercel akan otomatis mendeteksi konfigurasi dari vercel.json
4. Aplikasi akan di-deploy secara otomatis

## Dependencies

- flask>=2.3.3
- matplotlib>=3.8.0
- seaborn>=0.13.0

## Catatan

- Program menggunakan file CSV terpisah untuk setiap bidang
- Setiap bidang dibatasi 20 data peserta
- Visualisasi data dibuat secara dinamis menggunakan matplotlib dan seaborn
- Perhitungan statistik diimplementasikan secara manual menggunakan Python
- Program dapat di-deploy ke Vercel menggunakan konfigurasi vercel.json 