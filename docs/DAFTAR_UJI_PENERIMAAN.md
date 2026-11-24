# Daftar Uji Penerimaan Website V3

Catat hasil aktual setelah aplikasi dijalankan di browser. Jangan menandai lulus sebelum benar-benar diuji.

| No. | Skenario uji | Hasil yang diharapkan | Hasil aktual |
|---:|---|---|---|
| 1 | Jalankan `python tools/validasi_dataset.py` | Pemeriksaan struktur dan integritas lulus | Belum diuji oleh pengguna |
| 2 | Jalankan `streamlit run app.py` | Dashboard terbuka tanpa error | Belum diuji oleh pengguna |
| 3 | Pilih tahun 2021, 2022, dan 2023 | Filter tahun memperbarui ringkasan dan grafik | Belum diuji oleh pengguna |
| 4 | Pilih provinsi lalu kabupaten/kota | Opsi wilayah mengikuti filter provinsi | Belum diuji oleh pengguna |
| 5 | Pilih kelompok pangan | Grafik kelompok menampilkan baris agregat kelompok | Belum diuji oleh pengguna |
| 6 | Pilih komoditas | Grafik komoditas menampilkan baris komoditas, bukan baris agregat | Belum diuji oleh pengguna |
| 7 | Gunakan pencarian wilayah/komoditas | Data yang tidak cocok tersaring | Belum diuji oleh pengguna |
| 8 | Periksa nilai yang perlu tinjauan | Delapan nilai tidak masuk grafik pada pengaturan default | Belum diuji oleh pengguna |
| 9 | Periksa nilai tidak tersedia | Enam belas nilai tidak dianggap nol pada grafik | Belum diuji oleh pengguna |
| 10 | Buka halaman Data Konsumsi | Status dan catatan kualitas terlihat | Belum diuji oleh pengguna |
| 11 | Unduh hasil filter | CSV berisi seluruh baris hasil filter, bukan hanya pratinjau tabel | Belum diuji oleh pengguna |
| 12 | Perbandingan antarwilayah | Satu tahun dan satu indikator dibandingkan | Belum diuji oleh pengguna |
| 13 | Tren antarperiode | Hanya identitas wilayah konsisten yang ditawarkan untuk tren 2021–2023 | Belum diuji oleh pengguna |

Setelah setiap uji, isi kolom hasil aktual dan catat error/screenshot jika ada. Uji penerimaan fungsional ini terpisah dari evaluasi usability SUS oleh responden.
