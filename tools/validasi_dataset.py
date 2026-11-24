from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = (
    BASE_DIR / "data" / "final"
    / "19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv"
)

EXPECTED_STATUS = {
    "DAPAT_DIGUNAKAN": 52_393,
    "DAPAT_DIGUNAKAN_DENGAN_CATATAN": 11,
    "PERLU_TINJAUAN_SUMBER": 8,
    "TIDAK_TERSEDIA": 16,
}


def main() -> int:
    if not DATA_FILE.exists():
        print(f"GAGAL: dataset tidak ditemukan: {DATA_FILE}")
        return 1

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
    errors = []
    expected_cols = [
        "No", "Tahun", "Kode_Wilayah_BPS_Final16E",
        "Provinsi_BPS_Final16E", "Kabupaten_Kota_BPS_Final16E",
        "Kelompok_Bahan_Standar", "Komoditas_Standar",
        "Konsumsi_Pangan_Final", "Status_Final_Dataset_19",
        "Status_Kelayakan_Dashboard_19", "Catatan_Final_Dataset_19",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        errors.append(f"Kolom wajib tidak ditemukan: {missing}")

    if len(df) != 52_428:
        errors.append(f"Jumlah baris seharusnya 52.428, ditemukan {len(df):,}")

    if "Tahun" in df:
        years = pd.to_numeric(df["Tahun"], errors="coerce").value_counts().sort_index().to_dict()
        expected_years = {2021: 17_476, 2022: 17_476, 2023: 17_476}
        if years != expected_years:
            errors.append(f"Jumlah baris per tahun tidak sesuai: {years}")

    if "Kode_Wilayah_BPS_Final16E" in df and "Tahun" in df:
        regions = df.groupby("Tahun")["Kode_Wilayah_BPS_Final16E"].nunique().to_dict()
        if regions != {2021: 514, 2022: 514, 2023: 514}:
            errors.append(f"Jumlah kode wilayah unik per tahun tidak sesuai: {regions}")
        if df["Kode_Wilayah_BPS_Final16E"].isna().any():
            errors.append("Terdapat kode wilayah BPS kosong")

    if "Status_Kelayakan_Dashboard_19" in df:
        status = df["Status_Kelayakan_Dashboard_19"].value_counts().to_dict()
        if status != EXPECTED_STATUS:
            errors.append(f"Distribusi status kualitas tidak sesuai: {status}")

    if "Konsumsi_Pangan_Final" in df:
        values = pd.to_numeric(df["Konsumsi_Pangan_Final"], errors="coerce")
        if int(values.isna().sum()) != 16:
            errors.append(f"Jumlah nilai tidak tersedia seharusnya 16, ditemukan {int(values.isna().sum())}")
        if bool(values.lt(0).any()):
            errors.append("Terdapat nilai konsumsi final negatif")

    if all(c in df.columns for c in ["Tahun", "Kode_Wilayah_BPS_Final16E", "Kelompok_Bahan_Standar", "Komoditas_Standar"]):
        key = ["Tahun", "Kode_Wilayah_BPS_Final16E", "Kelompok_Bahan_Standar", "Komoditas_Standar"]
        duplicate_count = int(df.duplicated(key).sum())
        if duplicate_count:
            errors.append(f"Terdapat {duplicate_count} duplikasi kombinasi indikator-wilayah-tahun")

    print("AUDIT DATASET FINAL V2")
    print(f"File: {DATA_FILE.name}")
    print(f"Dimensi: {len(df):,} baris x {len(df.columns)} kolom")
    print("Baris/tahun: 2021=17.476 | 2022=17.476 | 2023=17.476")
    print("Wilayah unik/tahun: 514 pada masing-masing tahun")
    if errors:
        print("\nHASIL: GAGAL")
        for item in errors:
            print(f"- {item}")
        return 1
    print("HASIL: LULUS pemeriksaan struktur dan integritas yang ditetapkan")
    print("Catatan: lulus pemeriksaan otomatis tidak menggantikan peninjauan keputusan pemetaan dan catatan metodologis oleh peneliti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
