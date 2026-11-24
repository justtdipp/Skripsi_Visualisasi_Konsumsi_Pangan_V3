import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import io

from app import load_data, apply_main_filters, eligible_chart_rows, csv_bytes, DATA_FILE

print("=== TEST 1: LOAD DATA & STRUKTUR ===")
df = load_data(str(DATA_FILE))
print(f"Total baris: {len(df):,}, Kolom: {len(df.columns)}")
assert len(df) == 52428, "Baris tidak sesuai"
print("[PASS] Test 1: Load Data & Validasi Struktur")

print("\n=== TEST 2: FILTER TAHUN (2021, 2022, 2023) ===")
for y in ["2021", "2022", "2023"]:
    geo, grp, cmd, tbl = apply_main_filters(df, y, "Semua", "Semua", "Semua", "Semua", "")
    print(f"Tahun {y}: {len(geo):,} baris, Agregat Kelompok: {len(grp):,}, Komoditas: {len(cmd):,}")
    assert len(geo) == 17476, f"Tahun {y} baris salah"
    assert len(grp) == 4112, f"Tahun {y} baris agregat salah"
    assert len(cmd) == 13364, f"Tahun {y} baris komoditas salah"
print("[PASS] Test 2: Filter Tahun")

print("\n=== TEST 3: FILTER WILAYAH (PROVINSI & KAB/KOTA) ===")
geo, grp, cmd, tbl = apply_main_filters(df, "2023", "Jawa Barat", "Semua", "Semua", "Semua", "")
kab_count = geo["Kabupaten_Kota_BPS_Final16E"].nunique()
print(f"Jawa Barat 2023: {len(geo):,} baris, Kab/Kota unik: {kab_count}")
assert kab_count == 27, f"Jawa Barat kab/kota salah (ditemukan {kab_count})"

geo_kab, _, _, _ = apply_main_filters(df, "2023", "Jawa Barat", "Kabupaten Bogor", "Semua", "Semua", "")
print(f"Kabupaten Bogor 2023: {len(geo_kab)} baris")
assert len(geo_kab) == 34, "Satu kab/kota harusnya punya 34 baris (8 agregat + 26 komoditas)"
print("[PASS] Test 3: Filter Wilayah Berjenjang")

print("\n=== TEST 4: FILTER KELOMPOK PANGAN & KOMODITAS ===")
geo, grp, cmd, tbl = apply_main_filters(df, "2023", "Semua", "Semua", "Padi-padian", "Semua", "")
print(f"Padi-padian 2023: group_rows={len(grp)}, commodity_rows={len(cmd)}")
assert len(grp) == 514, "Baris agregat padi-padian 2023 harus 514"

geo, grp, cmd, tbl = apply_main_filters(df, "2023", "Semua", "Semua", "Padi-padian", "Beras", "")
print(f"Beras 2023: commodity_rows={len(cmd)}, table_rows={len(tbl)}")
assert len(cmd) == 514, "Baris komoditas beras 2023 harus 514"
assert not tbl["_is_agregat"].any(), "Table komoditas tidak boleh memuat agregat"
print("[PASS] Test 4: Filter Kelompok Pangan & Komoditas Mandiri")

print("\n=== TEST 5: PENCARIAN CEPAT (SEARCH QUERY) ===")
geo, grp, cmd, tbl = apply_main_filters(df, "Semua", "Semua", "Semua", "Semua", "Semua", "Sleman")
kab_sleman = [k.casefold() for k in geo["Kabupaten_Kota_BPS_Final16E"].unique()]
print(f"Pencarian 'Sleman': {len(geo)} baris, wilayah ditemukan: {geo['Kabupaten_Kota_BPS_Final16E'].unique()}")
assert any("sleman" in k for k in kab_sleman)
print("[PASS] Test 5: Pencarian Cepat Teks")

print("\n=== TEST 6: STATUS ANOMALI & DATA TIDAK TERSEDIA ===")
review_rows = df[df["Status_Kelayakan_Dashboard_19"] == "PERLU_TINJAUAN_SUMBER"]
missing_rows = df[df["Status_Kelayakan_Dashboard_19"] == "TIDAK_TERSEDIA"]
print(f"Perlu Tinjauan Sumber: {len(review_rows)} baris")
print(f"Tidak Tersedia: {len(missing_rows)} baris")
assert len(review_rows) == 8, "Harus tepat 8 baris tinjauan"
assert len(missing_rows) == 16, "Harus tepat 16 baris tidak tersedia"

default_chart = eligible_chart_rows(df, include_review=False)
with_review_chart = eligible_chart_rows(df, include_review=True)
print(f"Baris grafik default (exclude 8 review + 16 missing): {len(default_chart)} (Dikeluarkan: {len(df) - len(default_chart)})")
print(f"Baris grafik dengan checkbox aktif (exclude 16 missing): {len(with_review_chart)} (Dikeluarkan: {len(df) - len(with_review_chart)})")
assert len(df) - len(default_chart) == 24
assert len(df) - len(with_review_chart) == 16
print("[PASS] Test 6: Penanganan Anomali & Missing Value")

print("\n=== TEST 7: UNDUH CSV (DATA KONSUMSI) ===")
geo, grp, cmd, tbl = apply_main_filters(df, "2023", "Jawa Barat", "Semua", "Semua", "Semua", "")
data_bytes = csv_bytes(tbl)
df_downloaded = pd.read_csv(io.BytesIO(data_bytes))
print(f"Jumlah baris hasil unduhan CSV: {len(df_downloaded)}, Sesuai tabel: {len(tbl)}")
assert len(df_downloaded) == len(tbl)
print("[PASS] Test 7: Export / Unduh Dataset CSV")

print("\n=== TEST 8: PERBANDINGAN ANTARWILAYAH ===")
# Uji perbandingan default (exclude tinjauan sumber -> Sumba Timur nilai ekstrem dikecualikan: 513 wilayah)
comp_default = eligible_chart_rows(df[df["Tahun"] == 2023], include_review=False)
comp_grp_def = comp_default[comp_default["_is_agregat"] & (comp_default["Kelompok_Bahan_Standar"] == "Padi-padian")]
comp_summary_def = comp_grp_def.groupby("Kabupaten_Kota_BPS_Final16E", as_index=False)["Konsumsi_Pangan_Final"].mean()
print(f"Jumlah kab/kota dibandingkan pada tahun 2023 (Default, tanpa anomali): {len(comp_summary_def)}")
assert len(comp_summary_def) == 513, f"Harus 513 kab/kota (1 anomali dikecualikan), ditemukan {len(comp_summary_def)}"

# Uji perbandingan dengan sertakan tinjauan sumber -> 514 wilayah lengkap
comp_all = eligible_chart_rows(df[df["Tahun"] == 2023], include_review=True)
comp_grp_all = comp_all[comp_all["_is_agregat"] & (comp_all["Kelompok_Bahan_Standar"] == "Padi-padian")]
comp_summary_all = comp_grp_all.groupby("Kabupaten_Kota_BPS_Final16E", as_index=False)["Konsumsi_Pangan_Final"].mean()
print(f"Jumlah kab/kota dibandingkan pada tahun 2023 (Dengan anomali): {len(comp_summary_all)}")
assert len(comp_summary_all) == 514, f"Harus 514 kab/kota lengkap, ditemukan {len(comp_summary_all)}"

top10 = comp_summary_def.nlargest(10, "Konsumsi_Pangan_Final")
bottom10 = comp_summary_def.nsmallest(10, "Konsumsi_Pangan_Final")
print(f"Top 1 Konsumsi Padi-padian: {top10.iloc[0]['Kabupaten_Kota_BPS_Final16E']} ({top10.iloc[0]['Konsumsi_Pangan_Final']:.2f} kg/kapita/tahun)")
print(f"Bottom 1 Konsumsi Padi-padian: {bottom10.iloc[0]['Kabupaten_Kota_BPS_Final16E']} ({bottom10.iloc[0]['Konsumsi_Pangan_Final']:.2f} kg/kapita/tahun)")
print("[PASS] Test 8: Perbandingan Antarwilayah (Top 10 / Bottom 10)")

print("\n=== TEST 9: TREN ANTARPERIODE IDENTITAS STABIL ===")
identity_cols = ["Kode_Wilayah_BPS_Final16E", "Provinsi_BPS_Final16E", "Kabupaten_Kota_BPS_Final16E"]
counts = df[identity_cols + ["Tahun"]].drop_duplicates().groupby(identity_cols)["Tahun"].nunique()
stable = counts[counts == 3]
print(f"Jumlah wilayah dengan identitas konsisten 3 tahun (2021-2023): {len(stable)} wilayah")
assert len(stable) > 0
print("[PASS] Test 9: Filter Identitas Wilayah Stabil")

print("\n=======================================================")
print("SEMUA 9 SKENARIO UJI FUNGSIONAL (BLACK BOX) TELAH LULUS!")
print("=======================================================")
