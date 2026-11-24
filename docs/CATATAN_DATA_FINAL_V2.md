# Catatan Dataset Kerja Final V2

File aktif aplikasi: `data/final/19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv`.

## Ringkasan struktur yang diperiksa

| Pemeriksaan | Hasil |
|---|---:|
| Jumlah baris | 52.428 |
| Jumlah kolom | 35 |
| Baris tahun 2021 | 17.476 |
| Baris tahun 2022 | 17.476 |
| Baris tahun 2023 | 17.476 |
| Kode wilayah unik per tahun | 514 |
| Provinsi pada data 2021 | 34 |
| Provinsi pada data 2022 | 34 |
| Provinsi pada data 2023 | 38 |
| Baris agregat kelompok pangan | 12.336 (4.112 per tahun) |
| Baris komoditas penyusun | 40.092 |
| Kombinasi duplikat indikator-wilayah-tahun | 0 |
| Kode wilayah BPS kosong | 0 |
| Nilai konsumsi final negatif | 0 |
| Nilai konsumsi final tidak tersedia | 16 |

## Distribusi status kelayakan dashboard

| Status | Jumlah |
|---|---:|
| `DAPAT_DIGUNAKAN` | 52.393 |
| `DAPAT_DIGUNAKAN_DENGAN_CATATAN` | 11 |
| `PERLU_TINJAUAN_SUMBER` | 8 |
| `TIDAK_TERSEDIA` | 16 |

Status tersebut dipakai aplikasi untuk mengatur perlakuan visualisasi. Status `PERLU_TINJAUAN_SUMBER` tidak masuk grafik secara default, sedangkan `TIDAK_TERSEDIA` tidak diperlakukan sebagai nol. Nilai nol dari sumber tetap dipertahankan sebagai nol.

## Batasan interpretasi

1. Dashboard menyajikan rata-rata aritmetika observasi pada filter aktif; angka tersebut bukan total konsumsi nasional.
2. Perbandingan pada tingkat provinsi merupakan rata-rata sederhana observasi kabupaten/kota, bukan angka berbobot penduduk atau total konsumsi provinsi.
3. Jumlah provinsi berubah dari 34 pada 2021–2022 menjadi 38 pada 2023. Perbandingan antarperiode perlu memperhatikan konsistensi identitas wilayah.
4. Identitas wilayah pada kolom `*_Final16E` merupakan hasil standardisasi/pemetaan/rekonsiliasi pengolahan penelitian. Jangan menyebutnya sebagai pengesahan resmi BPS.
5. Terdapat kasus rekonsiliasi identitas yang didasarkan pada aturan/inferensi pengolahan. Peneliti tetap perlu merujuk register keputusan dan arsip audit saat menuliskan metodologi serta keterbatasan.
6. Lulus validasi otomatis tidak sama dengan persetujuan dosen pembimbing atau evaluasi usability.
