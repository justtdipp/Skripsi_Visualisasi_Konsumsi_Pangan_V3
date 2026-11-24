
from pathlib import Path
import pandas as pd

# Lokasi dataset
file_data = (
    Path(__file__).parent
    / "data"
    / "Dataset_Bapanas_Referensi_Wilayah_BPS.csv"
)

# Membaca dataset
df = pd.read_csv(file_data, encoding="utf-8-sig")

# Kolom yang diperiksa
kolom_kunci = ["Tahun", "Kode Wilayah"]
kolom_nama = [
    "Provinsi_BPS_Standar",
    "Kabupaten_Kota_BPS_Standar"
]

# Menghitung setiap kombinasi pemetaan wilayah
detail = (
    df.groupby(
        kolom_kunci + kolom_nama,
        dropna=False
    )
    .size()
    .reset_index(name="Jumlah_Baris")
)

# Menghitung jumlah pasangan nama untuk setiap kode
jumlah_pemetaan = (
    detail.groupby(kolom_kunci)
    .size()
    .reset_index(name="Jumlah_Pemetaan")
)

# Mengambil kode dengan lebih dari satu pasangan nama
kode_bermasalah = jumlah_pemetaan[
    jumlah_pemetaan["Jumlah_Pemetaan"] > 1
][kolom_kunci]

# Menyusun laporan rinci
laporan = detail.merge(
    kode_bermasalah,
    on=kolom_kunci,
    how="inner"
)

laporan = laporan.sort_values(
    kolom_kunci + kolom_nama
)

# Menyimpan laporan
file_output = (
    Path(__file__).parent
    / "data"
    / "Audit_Pemetaan_Wilayah.csv"
)

laporan.to_csv(
    file_output,
    index=False,
    encoding="utf-8-sig"
)

# Menampilkan ringkasan
print("PEMERIKSAAN PEMETAAN WILAYAH")
print("Jumlah kode dengan pemetaan berbeda:",
      len(kode_bermasalah))
print("Jumlah kombinasi pemetaan yang diperiksa:",
      len(laporan))
print("Laporan tersimpan di:", file_output)
print("\nRINCIAN PEMETAAN:")
print(laporan.to_string(index=False))