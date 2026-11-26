# LAPORAN BLACK BOX TESTING FINAL (READ-ONLY)
**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web (Versi 3)**

---

## 1. Identifikasi Lingkungan & Cakupan Audit
- **Tanggal Pengujian:** 26 November 2026
- **Mode Pengujian:** **READ-ONLY** (tidak ada modifikasi pada `app.py`, dataset CSV, konfigurasi, maupun laporan terdahulu).
- **Versi Lingkungan:**
  - Python: `3.14.4`
  - Streamlit: `1.67.0`
  - Pandas: `3.0.2`
  - Plotly: `7.1.0`
  - Pytest: `9.2.0`
  - Playwright: Terpasang (Chrome Headless)
- **Dataset Aktif:** `data/final/19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv` (`52.428` baris × `35` kolom).
- **Skrip Pengujian Baru (Terpisah di `tests/`):**
  - [`tests/test_dataset_readonly.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tests/test_dataset_readonly.py)
  - [`tests/test_blackbox_streamlit.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tests/test_blackbox_streamlit.py)
  - [`tests/test_browser_responsive.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tests/test_browser_responsive.py)
- **Log Pengujian Lengkap:** [`reports/blackbox_readonly_final/Log_Pengujian_Final.txt`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/Log_Pengujian_Final.txt)

---

## 2. Hasil Pengujian Integritas Dataset (Read-Only)
- **Dimensi & Periode:** `52.428` baris × `35` kolom; tahun `{2021, 2022, 2023}` dengan tepat `17.476` baris/tahun dan `514` wilayah unik/tahun (`4/4` pengujian di `test_dataset_readonly.py` **PASS**).
- **Kunci & Tipe Data:** `0` duplikasi kunci `(Tahun, Kode_Wilayah_BPS_Final16E, Kelompok_Bahan_Standar, Komoditas_Standar)`, `0` kode/nama wilayah kosong, `Tahun` bertipe integer, `Konsumsi_Pangan_Final` bertipe float, dan `0` nilai negatif.
- **Kualitas Data:**
  - `DAPAT_DIGUNAKAN`: `52.393` baris (termasuk `1.511` baris `NILAI_NOL_SUMBER`).
  - `DAPAT_DIGUNAKAN_DENGAN_CATATAN`: `11` baris (seluruhnya memiliki catatan audit).
  - `PERLU_TINJAUAN_SUMBER`: `8` baris (nilai ekstrem, dikecualikan dari grafik secara default).
  - `TIDAK_TERSEDIA`: `16` baris (seluruhnya bernilai `NaN`, tidak diisi `0`).

---

## 3. Matriks Pengujian Fungsional (BB-01 s.d. BB-21) & Desain (UI-01 s.d. UI-03)

| Kode Uji | Modul/Fitur | Skenario Uji | Expected Result | Actual Result | Status |
|:---:|:---|:---|:---|:---|:---:|
| **BB-01** | Pemuatan Aplikasi | Jalankan `streamlit run app.py` dan uji pemuatan via `AppTest` | Aplikasi terbuka tanpa exception & membaca dataset V2 | Server lokal `localhost:8501` merespons HTTP `200`; `AppTest` memuat tanpa exception dengan sidebar radio & 5+ selectbox | **PASS** |
| **BB-02** | Navigasi Halaman | Buka seluruh 3 menu navigasi via `AppTest` | Dashboard, Tabel Data Konsumsi, dan Tentang Data & Metodologi terbuka tanpa error | Ketiga halaman terbuka berurutan dengan `not at.exception` | **PASS** |
| **BB-03** | Filter Tahun | Pilih `2021`, `2022`, dan `2023` secara bergantian | Setiap tahun menghasilkan `17.476` baris (`4.112` agregat + `13.364` komoditas) | `2021=17.476`, `2022=17.476`, `2023=17.476`; interaksi `AppTest` tanpa error | **PASS** |
| **BB-04** | Filter Provinsi | Pilih provinsi `Aceh` dan `Jawa Barat` | Data dan opsi kab/kota mengikuti provinsi terpilih | `Aceh=23` kab/kota, `Jawa Barat=27` kab/kota; `AppTest` memuat `Kabupaten Aceh Barat Daya` dan mengecualikan `Kabupaten Bogor` | **PASS** |
| **BB-05** | Filter Kabupaten/Kota | Pilih `Aceh` → `Kabupaten Aceh Barat Daya` | Data hanya menampilkan wilayah terpilih (`34` indikator/tahun) | Menghasilkan tepat `34` baris (`8` agregat + `26` komoditas) untuk `Kabupaten Aceh Barat Daya` (2023) | **PASS** |
| **BB-06** | Validasi 6 Wilayah DKI Jakarta | Periksa kode `3101`, `3171`, `3172`, `3173`, `3174`, `3175` pada filter provinsi `DKI Jakarta` | Keenam wilayah termasuk Jakarta Utara ditemukan tanpa terhilang akibat label | Keenam kode hadir di `DKI Jakarta` (`Kabupaten Kepulauan Seribu`, `Kota Jakarta Selatan`, `Kota Jakarta Timur`, `Kota Jakarta Pusat`, `Kota Jakarta Barat`, `Kota Jakarta Utara`); catatan: label tampilan tanpa kata "Administrasi" | **PASS** |
| **BB-07** | Filter Kelompok Pangan | Pilih kelompok `Padi-padian` | Grafik kelompok memakai baris agregat (`514` baris pada 2023) | Menghasilkan `514` baris dengan seluruhnya `_is_agregat == True` | **PASS** |
| **BB-08** | Filter Komoditas | Pilih `Padi-padian` → `Beras` | Grafik komoditas memakai baris komoditas penyusun tanpa agregat | Menghasilkan `514` baris komoditas dengan `0` baris agregat | **PASS** |
| **BB-09** | Pencarian Cepat | Kata kunci `Sleman` dan `Beras` | Menampilkan hanya data yang cocok (`Sleman=102`, `Beras=1.542`) | `Sleman=102` baris (`Kabupaten Sleman`); `Beras=1.542` baris | **PASS** |
| **BB-10** | Grafik Kelompok Pangan | Render grafik kelompok pada default & tahun `2023` + `Jawa Barat` | Grafik Plotly terbentuk tanpa error & berubah sesuai filter | Terender tanpa exception pada `AppTest` dan browser (`5` grafik Plotly aktif) | **PASS** |
| **BB-11** | Grafik Komoditas | Pilih kelompok `Padi-padian` → `Beras` via `AppTest` | Grafik menampilkan komoditas sesuai filter & urutan tertinggi | Terender tanpa exception pada `AppTest` & browser | **PASS** |
| **BB-12** | Penanganan Nilai Tinjauan Sumber | Toggle checkbox `PERLU_TINJAUAN_SUMBER` | `8` nilai dikecualikan default & dapat disertakan via checkbox | Selisih baris layak grafik aktif vs default tepat `8` baris; toggle `AppTest` sukses | **PASS** |
| **BB-13** | Penanganan Nilai Tidak Tersedia | Periksa `16` baris berstatus `TIDAK_TERSEDIA` | Nilai tetap `NaN`, tidak dianggap `0`, tidak masuk grafik | Seluruh `16` baris bernilai `NaN`; `0` nilai `NaN` masuk grafik | **PASS** |
| **BB-14** | Tabel Data Konsumsi | Buka halaman `📋 Tabel Data Konsumsi` via `AppTest` | Seluruh `15` kolom tampil termasuk `Flag Anomali Sumber` & `Catatan Pembersihan Nilai` | Seluruh `15` kolom tampil lengkap (`Konsumsi Final`, `Nilai Mentah Sumber Asli`, `Status Kelayakan`, `Kategori Nilai Data`, `Flag Anomali Sumber`, `Catatan Pembersihan Nilai`, `Penjelasan Audit & Kualitas`, `Catatan Rekonsiliasi Wilayah`, dll.) | **PASS** |
| **BB-15** | Ekspor CSV | Ekspor seluruh dataset & filter `Jawa Barat` 2023 | CSV memuat seluruh baris filter (`52.428` dan `918`), bukan pratinjau `300` | CSV seluruh data=`52.428` baris; CSV Jabar 2023=`918` baris | **PASS** |
| **BB-16** | Perbandingan Antarwilayah | Tahun `2023`, `Kabupaten/Kota`, indikator `Padi-padian` | Top 10 & Bottom 10 pada tahun dan indikator sama tanpa duplikasi | `513` kab/kota unik (`1` anomali dikecualikan); Top 10 & Bottom 10 terbentuk | **PASS** |
| **BB-17** | Perbandingan Antarperiode | Cek daftar wilayah stabil `2021–2023` | Hanya wilayah identitas konsisten (`487` kab/kota) yang ditawarkan | Terdeteksi tepat `487` kabupaten/kota konsisten pada ketiga tahun | **PASS** |
| **BB-18** | Ringkasan KPI | Ubah filter tahun, provinsi, dan indikator | 4 kartu KPI diperbarui tanpa mencampur agregat & komoditas | 2023 agregat=`4.110` observasi (`38` provinsi); `Beras`=`514` observasi komoditas | **PASS** |
| **BB-19** | Konsistensi Filter | Ubah filter utama ke `2022` & `Aceh` via `AppTest` | Grafik utama ikut sidebar; perbandingan & tren pakai kontrol lokal | `compare_year_v2` dan `trend_region_v2` tetap independen tanpa konflik | **PASS** |
| **BB-20** | Informasi Metodologi & Kualitas | Buka halaman `ℹ️ Tentang Data & Metodologi` via `AppTest` | Sumber Bapanas, periode, satuan, `11` catatan, `8` tinjauan, `16` missing tampil benar | Seluruh informasi sumber, satuan `kg / kapita / tahun`, `1.511` nol, `16` missing, `8` anomali tampil | **PASS** |
| **BB-21** | Penanganan Kondisi Tanpa Hasil | Pencarian `KATA_KUNCI_TIDAK_ADA_XYZ` lalu reset `""` via `AppTest` | Menampilkan pesan info wajar tanpa crash dan pulih saat filter direset | Menampilkan pesan `Tidak ada nilai...` tanpa exception dan pulih normal saat direset | **PASS** |
| **UI-01** | Tema & Aset Visual | Uji browser Playwright atas `.stApp`, `.header-hero`, aset lokal | Aset lokal dimuat tanpa URL eksternal & tema gelap konsisten | `appBgColor=rgb(16, 27, 24)`, `appHasBgImage=true`, `heroHasBgImage=true`, `0` kegagalan request eksternal/console | **PASS** |
| **UI-02** | Keterbacaan & Interaksi | Uji kontras, kartu KPI, grafik Plotly, tabel, dan tombol unduh di browser | Teks terbaca, KPI tidak bertumpuk, seluruh kontrol aktif | `kpiCount=4`, `kpi_overlaps=[]`, `chartCount=5`, `chartOverflows=[]`, `dlBtnVisible=true`, `0` error | **PASS** |
| **UI-03** | Responsivitas Browser | Uji Playwright pada `1366×768`, `768×1024`, dan `390×844` | Tidak ada elemen terpotong/bertumpuk; grafik & tabel responsif | Halaman tidak overflow horizontal (`docScrollWidth == viewport` pada ketiga ukuran), `kpi_overlaps=[]`, `chartOverflows=[]`; terdapat catatan UX ringan | **PASS** |

---

## 4. Ringkasan Statistik, Peringatan Teknis & Temuan UX
- **Total Skenario:** `24` (`21` Fungsional `BB-01`..`BB-21` + `3` Desain `UI-01`..`UI-03`)
- **PASS:** `24`
- **FAIL:** `0`
- **BELUM DIUJI:** `0`
- **Peringatan Teknis (Non-Blokir):**
  1. Jika file CSV dibaca tanpa `low_memory=False` (seperti pada `pd.read_csv` standar), Pandas memunculkan `DtypeWarning` pada kolom catatan teks campuran (`Catatan_Rekonsiliasi_16E`); aplikasi utama sudah menanganinya dengan `low_memory=False`.
  2. Log Streamlit mencatat `DeprecationWarning` bahwa parameter `use_container_width` akan dihapus setelah `2025-12-31` (pengganti: `width='stretch'`).
- **Temuan Kualitas Data (Catatan Audit BB-06):**
  - Pada dataset final V2, enam wilayah DKI Jakarta (`3101`, `3171`, `3172`, `3173`, `3174`, `3175`) tampil dengan nama standar BPS tanpa kata `"Administrasi"` (mis. `Kota Jakarta Utara`, bukan `Kota Administrasi Jakarta Utara`). Keenamnya tetap lengkap dan tidak ada yang hilang saat pemfilteran.
- **Temuan UX Ringan (Non-Fungsional / Opsional):**
  1. Pada smartphone (`390×844 px`), `initial_sidebar_state="expanded"` menyebabkan drawer sidebar terbuka di awal hingga pengguna menekan tombol tutup `«`.
  2. Pada tablet (`768×1024 px`) dan smartphone (`390×844 px`), ketika sidebar dibiarkan terbuka di halaman Tabel Data Konsumsi, kontainer `stDataFrame` (`dfRightExceedsViewport: true`) menyentuh batas kanan viewport meski halaman tidak mengalami horizontal scroll (`docScrollWidthOnTable` tetap `768` dan `390`).

---

## 5. Bukti Tangkapan Layar Browser
Tersimpan di [`reports/blackbox_readonly_final/screenshots/`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/blackbox_readonly_final/screenshots/):
- `desktop_1366x768_dashboard.png` & `desktop_1366x768_tabel.png`
- `tablet_768x1024_dashboard.png` & `tablet_768x1024_tabel.png`
- `mobile_390x844_dashboard.png` & `mobile_390x844_tabel.png`

---

## 6. Kesimpulan Pengujian
1. **Kelulusan Fungsional (`BB-01` s.d. `BB-21` + Integritas Dataset):** **LULUS (21/21 PASS)**. Seluruh fitur filter, KPI, grafik, tabel 15 kolom, ekspor CSV, perbandingan wilayah/periode, dan penanganan kondisi kosong berjalan akurat tanpa mengubah dataset final V2.
2. **Kelulusan Desain & Responsivitas (`UI-01` s.d. `UI-03`):** **LULUS (3/3 PASS)** dengan 2 catatan UX ringan pada layar kecil.
3. **Rekomendasi Penyempurnaan Opsional (Tanpa Mengubah Kode Saat Audit):**
   - Pertimbangkan mengganti `initial_sidebar_state="expanded"` menjadi `"auto"` untuk pengalaman awal lebih lapang di smartphone.
   - Pertimbangkan mengganti `use_container_width=True` ke `width="stretch"` sebelum dukungan parameter lama dihapus oleh Streamlit.

