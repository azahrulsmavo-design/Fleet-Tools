# Fleet Management Tools Portal

Sebuah portal aplikasi web internal untuk menangani tugas-tugas operasional Fleet, dikembangkan dengan **Streamlit** dan **Python**, dan dirancang dengan arsitektur UI *Multi-page* yang ramping & scalable.

## Fitur Saat Ini
### 1. Bulk Fill PDF
Ketik atau menempelkan daftar **Nomor Polisi (Nopol)** dan tanggal surat, sistem akan secara otomatis:
- Mencocokkan data dengan data aset pada `MASTER.csv`. 
- Menulis (stamping) informasi *Merk, Tahun, Warna, No Rangka, No Mesin* ke dalam template PDF Fleet dengan pelurusan otomatis dan jenis huruf asli tanpa merusak gambar background template.
- Membundel seluruh rekaman PDF yang di-generate menjadi satu file `.zip` siap download.

## Instalasi dan Menjalankan Lokal

Karena bersifat aplikasi internal berbasis Python, ini instruksi untuk menjalankannya.

1. **Prasyarat**:
   Pastikan Anda menginstal Python 3.10+.
2. **Klon Repositori ini:**
   ```bash
   git clone https://github.com/azahrulsmavo-design/Fleet-Tools.git
   cd Fleet-Tools
   ```
3. **Instal Requirement Libraries:**
   Disarankan menggunakan virtual environment.
   ```bash
   pip install -r requirements.txt
   ```
4. **Siapkan Data & Template:**
   Pastikan file `MASTER.csv` dan `Template.pdf` berada di folder utama (sejajar dengan `app.py`). Karena repositori ini diset *private*, data armada aman untuk ikut tersimpan di GitHub.
5. **Jalankan Aplikasi:**
   ```bash
   streamlit run app.py
   ```
   Aplikasi dapat diakses via Web Browser di `http://localhost:8501:`.

## Menambahkan Tools Baru
Aplikasi didesain menggunakan fitur Multi-Pages. Jika kelak Anda ingin menambahkan Tool "Cek Perpanjangan Pajak", cukup buat file python baru di dalam folder `pages/` (Contoh: `pages/2_Pajak_Check.py`) dan ia akan langsung terdaftar di menu Navigasi utama sebelah kiri web.
