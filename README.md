# Sistem Informasi Visualisasi Konsumsi Pangan — V3

Versi pengembangan baru dari proyek Antigravity sebelumnya. Proyek lama disimpan di folder `arsip_proyek_lama`; aplikasi aktif di folder utama menggunakan dataset final V2.

## 1. Struktur proyek

- `app.py` — aplikasi Streamlit aktif.
- `data/final/19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv` — dataset kerja final yang dibaca aplikasi.
- `tools/validasi_dataset.py` — pemeriksaan dataset sebelum aplikasi dijalankan.
- `docs/` — catatan data dan daftar uji penerimaan.
- `arsip_proyek_lama/` — salinan proyek Antigravity yang dikirim, tidak dihapus dan tidak digunakan sebagai sumber data aktif.
- `.streamlit/config.toml` — konfigurasi tampilan.

## 2. Menjalankan di Windows dengan Antigravity IDE / VS Code

1. Ekstrak ZIP ini ke folder baru. Jangan menimpa folder proyek lama.
2. Buka folder `Skripsi_Visualisasi_Konsumsi_Pangan_V3` di Antigravity IDE.
3. Buka terminal pada folder utama proyek.
4. Buat environment baru dan instal dependensi:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Periksa dataset:

   ```powershell
   python tools/validasi_dataset.py
   ```

6. Jalankan aplikasi:

   ```powershell
   streamlit run app.py
   ```

7. Buka alamat lokal yang ditampilkan di terminal, biasanya `http://localhost:8501`.

Jika PowerShell menolak aktivasi environment, gunakan interpreter langsung:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tools\validasi_dataset.py
.venv\Scripts\python.exe -m streamlit run app.py
```

## 3. Fitur aplikasi

1. Filter tahun, provinsi, kabupaten/kota, kelompok pangan, dan komoditas.
2. Pencarian wilayah atau komoditas.
3. Ringkasan indikator dan cakupan data.
4. Grafik kelompok pangan memakai baris agregat kelompok.
5. Grafik komoditas memakai baris komoditas penyusun.
6. Perbandingan antarwilayah pada tahun dan indikator yang dipilih.
7. Tren 2021–2023 untuk identitas wilayah yang tersedia konsisten pada ketiga tahun.
8. Tabel data dengan status kualitas serta catatan pengolahan.
9. Unduh data hasil filter dan hasil perbandingan dalam CSV.
10. Halaman informasi sumber, periode, satuan, cakupan, dan batasan data.

## 4. Perlakuan kualitas data

- Grafik secara default memasukkan `DAPAT_DIGUNAKAN` dan `DAPAT_DIGUNAKAN_DENGAN_CATATAN`.
- `PERLU_TINJAUAN_SUMBER` dikecualikan dari grafik secara default; tersedia opsi untuk meninjaunya.
- `TIDAK_TERSEDIA` tidak diperlakukan sebagai nol dan tidak masuk perhitungan grafik.
- Nilai nol dari sumber tetap dipertahankan sebagai nilai nol.
- Baris agregat kelompok dipisahkan dari baris komoditas penyusun agar tidak terjadi penghitungan ganda.
- Rata-rata di dashboard merupakan rata-rata aritmetika observasi sesuai filter, bukan total konsumsi nasional.
- Perbandingan pada tingkat provinsi merupakan rata-rata sederhana observasi kabupaten/kota, bukan rata-rata berbobot penduduk atau total konsumsi provinsi.

## 5. Catatan penting

- Aplikasi membaca hanya file di `data/final/`. Dataset lama dan hasil Crosswalk tahap validasi tetap berada di `arsip_proyek_lama/` untuk ketertelusuran.
- Jangan menjalankan ulang `buat_crosswalk_bps.py` sebagai langkah untuk menjalankan website. Script tersebut adalah bagian dari proses pemetaan lama dan bukan proses pemuatan aplikasi.
- File CSV tidak dimodifikasi oleh aplikasi. Filter dan unduhan hanya menghasilkan tampilan/berkas hasil pilihan pengguna.
- Identitas wilayah adalah hasil standardisasi/pemetaan/rekonsiliasi pada pengolahan penelitian, bukan pengesahan resmi BPS. Kasus pemetaan dan keputusan yang memerlukan penjelasan tetap harus diterangkan di dokumen penelitian.
- Aplikasi dan daftar uji ini merupakan versi pengembangan untuk diuji. Pengujian browser sesungguhnya dan evaluasi usability oleh pengguna belum dinyatakan selesai sebelum hasil uji direkam.
