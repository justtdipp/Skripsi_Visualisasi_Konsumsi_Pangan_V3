# RINGKASAN BLACK BOX TESTING WEBSITE V3

**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web**

---

## Ringkasan Statistik Pengujian
- **Total Butir Pengujian:** 21 (`18` Fungsional + `3` Desain)
- **Jumlah PASS:** 21 (`18` Fungsional + `3` Desain)
- **Jumlah FAIL:** 0
- **Jumlah BELUM DIUJI:** 0

---

## Riwayat Perbaikan & Verifikasi Ulang
- **Skenario 12 (`test_11_tabel_data_konsumsi`):** Sebelumnya **FAIL** karena hanya menampilkan 13 kolom. Setelah menambahkan kembali `Flag_Anomali_Sumber_19` (*Flag Anomali Sumber*) dan `Catatan_Pembersihan_Nilai_18` (*Catatan Pembersihan Nilai*) ke `display_columns` pada `app.py`, pengujian ulang `pytest` menghasilkan **18/18 PASSED** dan verifikasi browser Playwright menampilkan tabel tanpa error.
- **Aspek Desain D3 (Responsivitas & Keterbacaan):** Terverifikasi **PASS** melalui Playwright (Chrome Headless) pada ukuran Desktop `1366×768`, Tablet `768×1024`, dan Smartphone `390×844` (dengan catatan UX opsional pada [`reports/Responsive_Browser_Testing_V3.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Responsive_Browser_Testing_V3.md)).

---

## Status Kelayakan Fungsional Website V3
**LULUS PENGUJIAN FUNGSIONAL (21/21 PASS)** — Seluruh skenario wajib telah diuji nyata dan tidak terdapat kegagalan yang belum diselesaikan.

---

## Berkas Laporan
- Laporan Lengkap: [`reports/Laporan_Black_Box_Testing_V3.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Laporan_Black_Box_Testing_V3.md)
- Tabel CSV (Excel): [`reports/Hasil_Black_Box_Testing_V3.csv`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Hasil_Black_Box_Testing_V3.csv)
- Laporan Responsif Browser: [`reports/Responsive_Browser_Testing_V3.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Responsive_Browser_Testing_V3.md)
- Log Eksekusi `pytest`: [`reports/Log_Pengujian_V3.txt`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Log_Pengujian_V3.txt)
