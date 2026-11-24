# LAPORAN BLACK BOX TESTING WEBSITE V3
**Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia Berbasis Web**

---

## 1. Pemeriksaan Awal Proyek
- **Dataset Aktif:** `data/final/19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv`
- **Hasil `python tools/validasi_dataset.py`:** `LULUS` (`52.428 baris × 35 kolom`, `514 wilayah unik/tahun`, `2021=17.476 | 2022=17.476 | 2023=17.476`).
- **Status Server Aplikasi:** `streamlit run app.py` aktif di `http://localhost:8501` dengan endpoint `/_stcore/health` merespons HTTP `200 OK`.
- **Metode Pengujian:** Otomatis via `pytest 9.2.0` + `streamlit.testing.v1.AppTest` ([`tools/test_blackbox_fungsional.py`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/tools/test_blackbox_fungsional.py)) dan verifikasi aset lokal.

---

## 2. Hasil Pengujian Fungsional (18 Skenario)

| No | Skenario | Input | Hasil yang Diharapkan | Hasil Aktual | Status | Catatan |
|:--:|:---|:---|:---|:---|:---:|:---|
| **1** | **Navigasi** | Buka 3 menu navigasi (`Dashboard Visualisasi`, `Tabel Data Konsumsi`, `Tentang Data & Metodologi`) via `AppTest` | Seluruh halaman dapat dibuka tanpa error | Ketiga halaman terbuka berurutan dengan `not at.exception` | **PASS** | `test_15_navigasi_halaman` |
| **2** | **Filter tahun** | Pilih tahun `2021`, `2022`, dan `2023` | Setiap tahun menghasilkan `17.476` baris (`4.112` agregat + `13.364` komoditas) | `2021=17.476`, `2022=17.476`, `2023=17.476`; `AppTest` selectbox sukses | **PASS** | `test_03_filter_tahun` |
| **3** | **Filter wilayah (provinsi)** | Pilih provinsi `Aceh` dan `Jawa Barat` | Opsi kab/kota dan visualisasi mengikuti provinsi terpilih | `Aceh=23` kab/kota, `Jawa Barat=27` kab/kota; `AppTest` menampilkan `Kabupaten Aceh Barat Daya` dan menyembunyikan `Kabupaten Bogor` | **PASS** | `test_04_filter_provinsi` |
| **4** | **Filter kabupaten/kota** | Pilih `Aceh` → `Kabupaten Aceh Barat Daya` | Data hanya menampilkan wilayah terpilih (`34` indikator/tahun) | Menghasilkan tepat `34` baris untuk `Kabupaten Aceh Barat Daya` (2023) | **PASS** | `test_05_filter_kabupaten_kota` |
| **5** | **Filter kelompok pangan** | Pilih kelompok `Padi-padian` | Grafik kelompok memakai baris agregat, bukan komoditas penyusun | `514` baris (2023), seluruhnya `_is_agregat == True` | **PASS** | `test_06_filter_kelompok_pangan` |
| **6** | **Filter komoditas** | Pilih `Padi-padian` → `Beras` | Grafik hanya memakai baris komoditas penyusun tanpa penghitungan ganda | `514` baris komoditas (2023), `0` baris agregat | **PASS** | `test_07_filter_komoditas` |
| **7** | **Pencarian cepat** | Kata kunci `Sleman` dan `Beras` | Hasil pencarian sesuai kata kunci (`Sleman` = `102` baris) | `Sleman=102` baris (`Kabupaten Sleman`); `Beras=1.542` baris | **PASS** | `test_08_pencarian_cepat` |
| **8** | **Grafik kelompok pangan** | Render grafik kelompok pangan pada filter default & tahun terpilih via `AppTest` | Grafik berubah mengikuti filter aktif (tren multi-tahun / bar per tahun) | Grafik terender tanpa exception dengan baris agregat murni | **PASS** | `test_02`, `test_03`, `test_06` |
| **9** | **Grafik komoditas** | Render 10 komoditas tertinggi sesuai filter via `AppTest` | Menampilkan 10 komoditas dengan konsumsi tertinggi tanpa baris agregat | Grafik bar horizontal terender tanpa exception | **PASS** | `test_02`, `test_07` |
| **10** | **Nilai perlu tinjauan** | Toggle checkbox penyertaan `8` nilai `PERLU_TINJAUAN_SUMBER` | Default dikecualikan dari grafik; saat dicentang masuk grafik | Selisih baris layak grafik antara aktif vs default tepat `8` baris | **PASS** | `test_09_nilai_perlu_tinjauan_sumber` |
| **11** | **Nilai tidak tersedia** | Periksa `16` baris berstatus `TIDAK_TERSEDIA` | Tetap kosong/`NaN`, tidak dianggap `0` | Seluruh `16` baris bernilai `NaN`; `0` nilai `NaN` masuk grafik | **PASS** | `test_10_nilai_tidak_tersedia` |
| **12** | **Tabel data** | Buka halaman `📋 Tabel Data Konsumsi` via `AppTest` & browser Playwright | Nilai konsumsi final, nilai sumber asli, status kelayakan, **flag anomali**, dan catatan kualitas tampil (`15` kolom) | Seluruh **15 kolom** tampil lengkap termasuk `Flag Anomali Sumber` (`Flag_Anomali_Sumber_19`) dan `Catatan Pembersihan Nilai` (`Catatan_Pembersihan_Nilai_18`); tampil rapi di browser (`0` error) | **PASS** | `test_11_tabel_data_konsumsi` |
| **13** | **Ekspor CSV** | Unduh seluruh dataset & filter `Jawa Barat` tahun `2023` | Seluruh baris sesuai filter diunduh (`52.428` dan `918`), bukan pratinjau `300` | CSV seluruh data=`52.428` baris; CSV Jabar 2023=`918` baris | **PASS** | `test_12_unduh_csv` |
| **14** | **Perbandingan antarwilayah** | Tahun `2023`, `Kabupaten/Kota`, indikator `Padi-padian` | Top 10 & Bottom 10 dihitung adil pada tahun & indikator sama | `513` kab/kota layak (`1` anomali dikecualikan), Top 10 & Bottom 10 terbentuk tanpa duplikasi | **PASS** | `test_13_perbandingan_antarwilayah` |
| **15** | **Perbandingan antarperiode** | Tren `2021–2023` wilayah stabil | Hanya menawarkan identitas wilayah konsisten (`487` kab/kota) | Terdeteksi tepat `487` kabupaten/kota stabil selama 3 tahun | **PASS** | `test_14_perbandingan_antarperiode` |
| **16** | **KPI** | Ubah filter tahun, provinsi, dan komoditas | 4 kartu KPI diperbarui sesuai filter tanpa mencampur agregat & komoditas | Filter 2023 agregat=`4.110` observasi (`38` provinsi); `Beras`=`514` observasi komoditas | **PASS** | `test_16_perhitungan_kpi` |
| **17** | **Konsistensi filter** | Ubah filter sidebar ke `2022` dan `Aceh` via `AppTest` | Grafik utama ikut sidebar; perbandingan wilayah & periode pakai kontrol lokal | `compare_year_v2` dan `trend_region_v2` tetap aktif independen tanpa konflik | **PASS** | `test_17_konsistensi_filter` |
| **18** | **Informasi metodologi & kualitas** | Buka halaman `ℹ️ Tentang Data & Metodologi` via `AppTest` | Sumber Bapanas, periode, satuan, `11` rekonsiliasi/koreksi, `8` tinjauan, `16` tidak tersedia | Seluruh informasi sumber, satuan `kg / kapita / tahun`, `1.511` nol, `16` missing, `8` anomali tampil | **PASS** | `test_18_informasi_kualitas_dan_metodologi` |

---

## 3. Hasil Pengujian Desain Terbaru (Dark Food Analytics & Observatory)

| No | Aspek Desain | Input / Metode Pemeriksaan | Hasil yang Diharapkan | Hasil Aktual | Status | Catatan |
|:--:|:---|:---|:---|:---|:---:|:---|
| **D1** | **Aset visual lokal & offline** | Eksekusi impor `BG_OBSERVATORY_URI`, `HERO_BANNER_URI`, `SIDEBAR_CONTOUR_URI` dari `app.py` | Aset lokal di `assets/` termuat tanpa koneksi eksternal | `bg_observatory.jpg` (data URI 116.091 char), `hero_food_banner.jpg` (145.351 char), `sidebar_contour.svg` (1.782 char) termuat | **PASS** | Tidak bergantung internet |
| **D2** | **Konfigurasi tema gelap** | Inspeksi `.streamlit/config.toml` & `PLOTLY_THEME_LAYOUT` di `app.py` | Tema gelap (`#101B18`, `#172923`, `#F3F4EF`) dan layout Plotly gelap terpasang | `base = "dark"` aktif di `config.toml`; `PLOTLY_THEME_LAYOUT` terpasang pada seluruh grafik | **PASS** | Konsisten di kode |
| **D3** | **Keterbacaan, kontras, tumpang tindih & responsivitas layar** | Pengujian Playwright (Chrome headless) pada `1366×768`, `768×1024`, dan `390×844` + inspeksi tangkapan layar | Teks/grafik/tabel mudah dibaca, tidak bertumpuk, responsif di desktop & layar kecil | Tidak ada overlap KPI (`[]`), tidak ada overflow grafik (`[]`), halaman tidak overflow horizontal (`docScrollWidth == viewport`), tabel & tombol unduh tampil dengan `0` console/page error | **PASS** | Catatan UX opsional di [`reports/Responsive_Browser_Testing_V3.md`](file:///c:/Users/dhifa/OneDrive/Dokumen/Desktop/TugasKuliah/Skripsi_Visualisasi_Konsumsi_Pangan_V3/reports/Responsive_Browser_Testing_V3.md) |

---

## 4. Riwayat Perbaikan Temuan
1. **Temuan #1 (Skenario 12 — Awalnya FAIL → Sekarang PASS):**
   - **Perbaikan yang Diterapkan:** Menambahkan kembali `"Flag_Anomali_Sumber_19"` (*Flag Anomali Sumber*) dan `"Catatan_Pembersihan_Nilai_18"` (*Catatan Pembersihan Nilai*) ke dalam `display_columns` dan `.rename(...)` pada `PAGE 2 — DATA KONSUMSI` di `app.py`, lalu menguji ulang via `pytest` (`18 passed`) dan Playwright (`0` error).

---

## 5. Kesimpulan Akhir
- **Total Butir Pengujian:** `21` (`18` Fungsional + `3` Desain)
- **Jumlah PASS:** `21` (`18` Fungsional + `3` Desain)
- **Jumlah FAIL:** `0`
- **Jumlah BELUM DIUJI:** `0`
- **Status Kelayakan Fungsional Website V3:** **LULUS PENGUJIAN FUNGSIONAL (21/21 PASS)** — Seluruh 18 skenario fungsional dan 3 aspek desain telah diuji nyata dan dinyatakan lulus tanpa kegagalan tersisa.
