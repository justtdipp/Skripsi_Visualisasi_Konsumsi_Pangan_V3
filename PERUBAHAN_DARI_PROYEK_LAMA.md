# Perubahan Proyek Lama ke V3

1. Proyek Antigravity yang dikirim tetap disimpan di `arsip_proyek_lama/` dan tidak ditimpa.
2. `app.py` aktif pada folder utama telah diarahkan ke dataset final V2 di `data/final/`.
3. Aplikasi memakai kolom konsumsi final `Konsumsi_Pangan_Final`, identitas wilayah `*_Final16E`, dan status kualitas `Status_Kelayakan_Dashboard_19`.
4. Pemeriksaan startup ditambah untuk mendeteksi dataset yang salah versi, distribusi status yang tidak sesuai, kode wilayah kosong, kombinasi duplikat, nilai negatif, dan jumlah baris agregat.
5. Arsip dataset tahap Crosswalk dan script pemetaan lama tidak dihapus dan tidak dipakai aplikasi aktif.
6. Ditambahkan utilitas validasi dataset, panduan instalasi, catatan batasan interpretasi, dan daftar uji penerimaan.

Aplikasi belum dapat dinyatakan teruji di lingkungan Antigravity pengguna sampai dijalankan di browser dan seluruh skenario uji dicatat.
