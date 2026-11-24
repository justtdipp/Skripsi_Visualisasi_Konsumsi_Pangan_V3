# Daftar Uji Penerimaan Website V3 (Hasil Pengujian Fungsional / Black Box Testing)

Pengujian fungsional black box dilakukan untuk memverifikasi kesesuaian sistem terhadap masukan (input) dan luaran (output) pada setiap modul antarmuka pengguna tanpa memodifikasi integritas data sumber.

| No. | Skenario uji | Hasil yang diharapkan | Hasil aktual | Status |
|---:|---|---|---|:---:|
| 1 | Jalankan `python tools/validasi_dataset.py` | Pemeriksaan struktur dan integritas lulus | Lulus seluruh pemeriksaan integritas (52.428 baris x 35 kolom, 514 wilayah/tahun) | **LULUS (PASS)** |
| 2 | Jalankan `streamlit run app.py` | Dashboard terbuka tanpa error | Server berjalan normal di port 8501, status HTTP 200 OK | **LULUS (PASS)** |
| 3 | Pilih tahun 2021, 2022, dan 2023 | Filter tahun memperbarui ringkasan dan grafik | Tepat menghasilkan 17.476 baris per tahun (4.112 agregat kelompok, 13.364 komoditas) | **LULUS (PASS)** |
| 4 | Pilih provinsi lalu kabupaten/kota | Opsi wilayah mengikuti filter provinsi | Pilihan kabupaten/kota dinamis (contoh: Jawa Barat memfilter tepat 27 kab/kota, 1 kab/kota tepat 34 baris) | **LULUS (PASS)** |
| 5 | Pilih kelompok pangan | Grafik kelompok menampilkan baris agregat kelompok | Tepat memfilter baris agregat kelompok (misal Padi-padian 2023 tepat 514 baris agregat) | **LULUS (PASS)** |
| 6 | Pilih komoditas | Grafik komoditas menampilkan baris komoditas, bukan baris agregat | Hanya baris komoditas penyusun yang dihitung, baris agregat tidak tercampur ganda | **LULUS (PASS)** |
| 7 | Gunakan pencarian wilayah/komoditas | Data yang tidak cocok tersaring | Pencarian teks (contoh: "Sleman") berhasil menyaring tepat 102 baris (3 tahun x 34 indikator) | **LULUS (PASS)** |
| 8 | Periksa nilai yang perlu tinjauan | Delapan nilai tidak masuk grafik pada pengaturan default | 8 baris anomali dikecualikan otomatis dari grafik; jika checkbox diaktifkan, masuk grafik | **LULUS (PASS)** |
| 9 | Periksa nilai tidak tersedia | Enam belas nilai tidak dianggap nol pada grafik | 16 baris `TIDAK_TERSEDIA` dipertahankan kosong/NaN (tidak diisi nol) pada visualisasi | **LULUS (PASS)** |
| 10 | Buka halaman Data Konsumsi | Status dan catatan kualitas terlihat | Tabel menyajikan 15 kolom lengkap mencakup status kelayakan, catatan audit, dan transparansi | **LULUS (PASS)** |
| 11 | Unduh hasil filter | CSV berisi seluruh baris hasil filter, bukan hanya pratinjau tabel | Berhasil mengunduh seluruh baris hasil filter (contoh Jawa Barat 2023 mengunduh 918 baris utuh) | **LULUS (PASS)** |
| 12 | Perbandingan antarwilayah | Satu tahun dan satu indikator dibandingkan | Grafik Top 10 dan Bottom 10 terisolasi per tahun & per indikator (contoh Padi-padian 2023) | **LULUS (PASS)** |
| 13 | Tren antarperiode | Hanya identitas wilayah konsisten yang ditawarkan untuk tren 2021–2023 | Terdeteksi tepat 487 kabupaten/kota stabil 3 tahun; wilayah pemekaran tidak dipaksakan ke tren | **LULUS (PASS)** |

---
*Catatan Pengujian: Skrip otomatisasi pengujian fungsional tersimpan pada `tools/test_blackbox_fungsional.py`.*
