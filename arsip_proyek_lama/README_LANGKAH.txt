PANDUAN OTOMATIS PEMETAAN WILAYAH BAPANAS - BPS 2021-2023

TUJUAN
Skrip ini mengambil referensi kode dan nama wilayah BPS per tahun melalui API wilayah Sipedas yang dokumentasinya menyatakan sumber data wilayah berasal dari BPS RI dan diperbarui setiap tahun. Skrip kemudian mencocokkan nama wilayah sumber Bapanas dengan referensi tahunan.

PENTING
- Dataset sumber tidak ditimpa.
- Nilai konsumsi tidak diubah, dihapus, atau diganti.
- Pemetaan berdasarkan nama/identitas wilayah; kode Bapanas disimpan terpisah dari kode BPS.
- Hasil ini adalah tahap crosswalk/validasi, belum otomatis menjadi dataset final.
- Baris yang tidak unik atau memiliki konflik akan diberi status perlu tinjauan.

LANGKAH
1. Ekstrak paket ini.
2. Salin file buat_crosswalk_bps.py ke folder utama proyek Streamlit, sejajar dengan app.py.
3. Pastikan dataset sumber berada di folder data dengan nama:
   Dataset_Bapanas_Referensi_Wilayah_BPS.csv
   Skrip juga mengenali nama file dengan akhiran (1).
4. Buka terminal VS Code di folder proyek.
5. Aktifkan virtual environment:
   .\.venv\Scripts\Activate.ps1
6. Instal kebutuhan jika belum ada:
   python -m pip install pandas requests
7. Jalankan:
   python buat_crosswalk_bps.py
8. Hasil otomatis tersimpan di:
   data\hasil_validasi\

FILE OUTPUT UTAMA
- Crosswalk_Bapanas_BPS_2021_2023.csv
- Dataset_Bapanas_Hasil_Crosswalk_Tahap_Validasi.csv
- Lokasi_Perlu_Tinjauan.csv
- Ringkasan_Hasil_Crosswalk.csv
- Referensi_Wilayah_BPS_2021_2023.csv

SETELAH BERHASIL
Tidak perlu membuka setiap file. Unggah kembali kepada ChatGPT hanya:
1. Ringkasan_Hasil_Crosswalk.csv
2. Lokasi_Perlu_Tinjauan.csv
3. Crosswalk_Bapanas_BPS_2021_2023.csv

Dengan tiga file tersebut, hasil pemetaan dapat dievaluasi sebelum app.py diubah.

SUMBER API
https://sipedas.pertanian.go.id/api/wilayah/index
Dokumentasi menyebut API wilayah bersumber dari BPS RI, diperbarui per tahun, dan meminta parameter tahun serta level wilayah. API dapat tidak stabil; skrip mencoba ulang hingga empat kali.
