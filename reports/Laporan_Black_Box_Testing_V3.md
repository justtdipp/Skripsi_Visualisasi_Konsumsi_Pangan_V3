# LAPORAN PENGUJIAN FUNGSIONAL (BLACK BOX TESTING) WEBSITE V3
**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web**

---

## 1. Informasi Umum Pengujian
- **Tanggal Pengujian:** 25 November 2026
- **Versi Sistem:** Website V3 (Tema *Indonesian Food & Agriculture Data Observatory* / *Dark Food Analytics*)
- **Dataset Acuan:** `data/final/19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv` (52.428 baris × 35 kolom)
- **Metode Pengujian:** Pengujian Kotak Hitam (*Black Box Testing*) otomatis menggunakan `pytest 9.2.0` dan `streamlit.testing.v1.AppTest` melalui skrip [`tools/test_blackbox_fungsional.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tools/test_blackbox_fungsional.py).
- **Log Eksekusi Lengkap:** [`reports/Log_Pengujian_V3.txt`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Log_Pengujian_V3.txt)

---

## 2. Hasil Pengujian 18 Skenario Wajib

| No | Skenario Uji | Input / Aksi | Hasil yang Diharapkan | Hasil Aktual | Status | Keterangan |
|:--:|:---|:---|:---|:---|:---:|:---|
| **1** | Validasi dataset final V2 | Menjalankan `python tools/validasi_dataset.py` | 52.428 baris, 35 kolom, 514 wilayah/tahun, 0 duplikasi, 0 kode kosong, 0 nilai negatif | 52.428 baris × 35 kolom, 514 wilayah/tahun, keluaran `HASIL: LULUS` | **PASS** | Dataset V2 utuh & valid |
| **2** | Menjalankan aplikasi Streamlit | Memuat `app.py` via `AppTest` | Aplikasi dimuat tanpa error, seluruh komponen sidebar aktif | Tidak ada exception; 5+ selectbox dan navigasi radio termuat | **PASS** | Siap dijalankan |
| **3** | Pengujian filter tahun | Memilih tahun `2021`, `2022`, `2023` secara bergantian | 17.476 baris/tahun (4.112 agregat + 13.364 komoditas), tidak tercampur tahun lain | 2021=17.476, 2022=17.476, 2023=17.476; interaksi `AppTest` sukses tanpa error | **PASS** | Filter tahun akurat |
| **4** | Pengujian filter provinsi | Memilih `Aceh` dan `Jawa Barat` | Data & opsi kab/kota hanya memuat wilayah provinsi terpilih | Aceh=23 kab/kota, Jawa Barat=27 kab/kota; `AppTest` memuat `Kabupaten Aceh Barat Daya` & mengecualikan `Kabupaten Bogor` | **PASS** | Hierarki wilayah berjalan |
| **5** | Pengujian filter kabupaten/kota | Memilih `Aceh` → `Kabupaten Aceh Barat Daya` | Data hanya dari kab/kota terpilih dengan 34 indikator/tahun | Menghasilkan tepat 34 baris untuk tahun 2023 khusus `Kabupaten Aceh Barat Daya` | **PASS** | Sesuai struktur 34 indikator |
| **6** | Pengujian filter kelompok pangan | Memilih kelompok `Padi-padian` | Grafik kelompok menggunakan baris agregat (514 observasi pada 2023) | Menghasilkan 514 baris dan seluruhnya bertipe `_is_agregat == True` | **PASS** | Bebas pencampuran komoditas |
| **7** | Pengujian filter komoditas | Memilih kelompok `Padi-padian` → komoditas `Beras` | Grafik komoditas hanya memakai baris komoditas penyusun tanpa agregat | Menghasilkan 514 baris komoditas dan 0 baris agregat pada grafik/tabel | **PASS** | Bebas *double-counting* |
| **8** | Pengujian pencarian cepat | Kata kunci `Sleman` dan `Beras` | `Sleman` = 102 baris (3 thn × 34); pencarian komoditas berfungsi | `Sleman`=102 baris (khusus `Kabupaten Sleman`); `Beras`=1.542 baris | **PASS** | Pencarian parsial akurat |
| **9** | Pengujian nilai perlu tinjauan sumber | Mengaktifkan/menonaktifkan checkbox tinjauan sumber | 8 nilai `PERLU_TINJAUAN_SUMBER` dikecualikan default & masuk saat aktif | Selisih baris layak grafik antara aktif vs default tepat 8 baris | **PASS** | Transparansi anomali terjaga |
| **10** | Pengujian nilai tidak tersedia | Memeriksa 16 baris `TIDAK_TERSEDIA` | Nilai tetap `NaN`, tidak diubah jadi `0`, tidak masuk grafik | 16 baris seluruhnya `NaN`; 0 nilai `NaN` masuk grafik | **PASS** | Tidak dianggap nol |
| **11** | Pengujian tabel Data Konsumsi | Membuka halaman `📋 Tabel Data Konsumsi` via `AppTest` | Seluruh **15 kolom** tabel tersedia termasuk `Flag_Anomali_Sumber_19` dan `Catatan_Pembersihan_Nilai_18` | Tabel hanya menampilkan **13 kolom**. Kolom `Flag_Anomali_Sumber_19` dan `Catatan_Pembersihan_Nilai_18` tidak tercantum di `display_columns` `app.py` | **FAIL** | **Temuan:** 2 kolom audit tidak tampil di halaman tabel |
| **12** | Pengujian unduh CSV | Ekspor seluruh dataset & filter `Jawa Barat` tahun `2023` | Seluruh baris & kolom ikut diekspor (Jabar 2023 = 918 baris, tidak terpotong 300 pratinjau) | CSV seluruh data=52.428 baris; CSV Jabar 2023=918 baris dengan jumlah kolom utuh | **PASS** | Ekspor penuh sesuai filter |
| **13** | Pengujian perbandingan antarwilayah | Tahun `2023`, tingkat `Kabupaten/Kota`, indikator `Padi-padian` | Perbandingan adil 1 tahun 1 indikator, Top 10 & Bottom 10 tanpa duplikasi | 513 kab/kota layak (1 anomali dikecualikan), Top 10 & Bottom 10 masing-masing 10 baris | **PASS** | Perbandingan akurat |
| **14** | Pengujian perbandingan antarperiode | Memilih wilayah stabil untuk tren `2021–2023` | Hanya 487 kab/kota konsisten 3 tahun yang ditawarkan | Terdeteksi tepat 487 identitas wilayah stabil 3 tahun penuh | **PASS** | Wilayah pemekaran tidak dipaksakan |
| **15** | Pengujian navigasi halaman | Membuka 3 menu navigasi via `AppTest` | `Dashboard Visualisasi`, `Tabel Data Konsumsi`, `Tentang Data & Metodologi` terbuka tanpa error | Ketiga halaman berhasil dibuka berurutan dengan `not at.exception` | **PASS** | Navigasi stabil |
| **16** | Pengujian KPI | Mengubah filter tahun, provinsi, dan komoditas | KPI diperbarui akurat, tidak mencampur agregat & komoditas | Filter 2023 seluruh kelompok=4.110 observasi agregat (38 provinsi); filter `Beras`=514 observasi komoditas | **PASS** | Perhitungan KPI presisi |
| **17** | Pengujian konsistensi filter | Mengubah filter utama ke `2022` dan `Aceh` via `AppTest` | Filter utama mengatur KPI/grafik 1–2; modul perbandingan & tren mempertahankan kontrol lokal | `compare_year_v2` dan `trend_region_v2` tetap aktif independen tanpa konflik | **PASS** | Tidak ada konflik filter |
| **18** | Pengujian informasi kualitas & metodologi | Membuka halaman `ℹ️ Tentang Data & Metodologi` via `AppTest` | Penjelasan sumber Bapanas, satuan `kg/kapita/tahun`, 1.511 nol, 16 missing, 8 anomali, 11 catatan | Seluruh informasi sumber, satuan, kategori nol/kosong/ekstrem, dan batasan tampil lengkap | **PASS** | Informasi edukatif lengkap |

---

## 3. Daftar Temuan & Usulan Perbaikan

### Temuan #1 — Skenario 11 (`test_11_tabel_data_konsumsi`): **FAIL**
- **Lokasi:** `app.py` (bagian `PAGE 2 — DATA KONSUMSI`, variabel `display_columns` dan `rename`).
- **Penyebab:** Saat penyederhanaan kolom tabel dilakukan sebelumnya, dua kolom audit yaitu `Flag_Anomali_Sumber_19` dan `Catatan_Pembersihan_Nilai_18` terhapus dari daftar `display_columns`, sehingga tabel hanya menampilkan **13 kolom** alih-alih **15 kolom** sebagaimana tercantum pada spesifikasi skenario uji.
- **Dampak:** Pengguna tidak dapat melihat kolom *Flag Anomali Sumber* dan *Catatan Pembersihan Nilai* secara langsung di tabel maupun file unduhan halaman `Tabel Data Konsumsi`.
- **Usulan Perbaikan:** Tambahkan kembali `"Flag_Anomali_Sumber_19"` dan `"Catatan_Pembersihan_Nilai_18"` ke `display_columns` serta tambahkan pemetaan labelnya pada `.rename(columns={...})` di `app.py` (misal `"Flag Anomali Sumber"` dan `"Catatan Pembersihan Nilai"`), lalu jalankan ulang `pytest tools/test_blackbox_fungsional.py -v`.

---

## 4. Kesimpulan Pengujian
- **Total Skenario Pengujian:** 18
- **Jumlah PASS:** 17
- **Jumlah FAIL:** 1 (`test_11_tabel_data_konsumsi`)
- **Jumlah BELUM DIUJI:** 0
- **Status Kelayakan Fungsional Website V3:** **BELUM LULUS PENUH (1 TEMUAN PERLU DIPERBAIKI)** — Sesuai ketentuan pengujian, website baru dapat dinyatakan lulus penuh setelah Temuan #1 pada Skenario 11 disetujui untuk diperbaiki dan diuji ulang hingga berstatus PASS.
