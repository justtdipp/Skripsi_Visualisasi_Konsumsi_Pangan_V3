# RINGKASAN BLACK BOX TESTING FINAL (READ-ONLY)
**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web (V3)**

---

## Ringkasan Statistik Pengujian
- **Total Skenario Pengujian:** 24 (`BB-01` s.d. `BB-21` Fungsional + `UI-01` s.d. `UI-03` Desain & Responsivitas)
- **Jumlah PASS:** 24
- **Jumlah FAIL:** 0
- **Jumlah BELUM DIUJI:** 0
- **Pengujian Integritas Dataset (`test_dataset_readonly.py`):** 4/4 PASS (`52.428` baris × `35` kolom, `514` wilayah/tahun, `0` duplikasi, `0` nilai negatif)

---

## Peringatan Teknis & Temuan Kualitas Data
1. **DtypeWarning (Non-Blokir):** Pembacaan CSV tanpa `low_memory=False` memicu peringatan tipe campuran pada `Catatan_Rekonsiliasi_16E`; `app.py` sudah menanganinya dengan `low_memory=False`.
2. **DeprecationWarning Streamlit:** `use_container_width` di `app.py` akan dihapus setelah `2025-12-31` (rekomendasi opsional: ganti ke `width="stretch"`).
3. **Nama Standar DKI Jakarta (BB-06):** Keenam kode wilayah (`3101`, `3171`, `3172`, `3173`, `3174`, `3175`) hadir lengkap di provinsi `DKI Jakarta`, dengan penamaan BPS tanpa kata `"Administrasi"`.
4. **Temuan UX Ringan (UI-03):** Pada smartphone (`390×844`), sidebar terbuka di awal (`initial_sidebar_state="expanded"`) hingga ditutup pengguna, dan pada tablet/smartphone kontainer `stDataFrame` menyentuh batas kanan saat sidebar terbuka.

---

## Kesimpulan Kelayakan
- **Kelulusan Fungsional:** **LULUS (21/21 PASS)**
- **Kelulusan Desain & Responsivitas:** **LULUS (3/3 PASS)**

---

## Berkas Laporan
- Laporan Lengkap: [`Laporan_Black_Box_Final.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/Laporan_Black_Box_Final.md)
- Tabel CSV (Excel): [`Hasil_Black_Box_Final.csv`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/Hasil_Black_Box_Final.csv)
- Log Pengujian: [`Log_Pengujian_Final.txt`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/Log_Pengujian_Final.txt)
- Tangkapan Layar: [`screenshots/`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/screenshots/)

