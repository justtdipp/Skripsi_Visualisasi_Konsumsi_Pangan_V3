# RINGKASAN BLACK BOX TESTING WEBSITE V3

**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web**

---

## Ringkasan Statistik Pengujian
- **Total Skenario Pengujian:** 18
- **Jumlah PASS:** 17
- **Jumlah FAIL:** 1
- **Jumlah BELUM DIUJI:** 0

---

## Daftar Temuan yang Harus Diperbaiki
1. **Skenario 11 (`test_11_tabel_data_konsumsi`) — FAIL:**
   - **Masalah:** Halaman `📋 Tabel Data Konsumsi` pada `app.py` saat ini hanya menampilkan **13 kolom** (`display_columns`), karena kolom `Flag_Anomali_Sumber_19` dan `Catatan_Pembersihan_Nilai_18` tidak disertakan.
   - **Usulan Perbaikan:** Mengembalikan kedua kolom audit tersebut ke dalam `display_columns` dan `.rename(columns={...})` pada `app.py` agar seluruh **15 kolom** tabel dapat diperiksa oleh pengguna.

---

## Status Kelayakan Fungsional Website V3
**BELUM LULUS PENUH** — Terdapat **1 kegagalan (FAIL)** pada Skenario 11 yang perlu disetujui untuk diperbaiki dan diuji ulang sebelum website dinyatakan lulus 100%.

---

## Berkas Terkait
- Laporan Lengkap: [`reports/Laporan_Black_Box_Testing_V3.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Laporan_Black_Box_Testing_V3.md)
- Tabel CSV (Excel): [`reports/Hasil_Black_Box_Testing_V3.csv`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Hasil_Black_Box_Testing_V3.csv)
- Log Eksekusi Otomatis: [`reports/Log_Pengujian_V3.txt`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Log_Pengujian_V3.txt)
- Skrip Pengujian `pytest`: [`tools/test_blackbox_fungsional.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tools/test_blackbox_fungsional.py)
