"""
Pengujian Fungsional (Black Box Testing) Website V3
Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia

Menggunakan pytest dan streamlit.testing.v1.AppTest untuk menguji
seluruh 18 skenario wajib pada dataset final V2 tanpa mengubah data sumber.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import (
    DATA_FILE,
    QUALITY_LABEL_MAP,
    STATUS_ELIGIBLE,
    STATUS_FINAL_LABEL_MAP,
    STATUS_MISSING,
    STATUS_REVIEW,
    apply_main_filters,
    csv_bytes,
    eligible_chart_rows,
    load_data,
)


@pytest.fixture(scope="module")
def dataset() -> pd.DataFrame:
    return load_data(str(DATA_FILE))


def test_01_validasi_dataset_v2():
    """Skenario 1: Validasi dataset final V2 melalui tools/validasi_dataset.py."""
    proc = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tools" / "validasi_dataset.py")],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    assert proc.returncode == 0, f"Validasi gagal: {proc.stderr}"
    assert "52,428 baris x 35 kolom" in proc.stdout
    assert "514 pada masing-masing tahun" in proc.stdout
    assert "HASIL: LULUS" in proc.stdout


def test_02_menjalankan_aplikasi_streamlit():
    """Skenario 2: Menjalankan aplikasi Streamlit via AppTest tanpa error."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Aplikasi mengalami exception: {at.exception}"
    assert len(at.sidebar.selectbox) >= 5
    assert len(at.sidebar.radio) >= 1


def test_03_filter_tahun(dataset: pd.DataFrame):
    """Skenario 3: Pengujian filter tahun 2021, 2022, dan 2023."""
    for yr in ("2021", "2022", "2023"):
        geo, grp, cmd, _ = apply_main_filters(dataset, yr, "Semua", "Semua", "Semua", "Semua", "")
        assert len(geo) == 17_476
        assert len(grp) == 4_112
        assert len(cmd) == 13_364
        assert set(geo["Tahun"].dropna().astype(int).unique()) == {int(yr)}

    # Verifikasi interaksi AppTest pada selectbox Tahun
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[0].set_value("2023").run()
    assert not at.exception


def test_04_filter_provinsi(dataset: pd.DataFrame):
    """Skenario 4: Pengujian filter provinsi (Aceh dan Jawa Barat)."""
    for prov, expected_kab in (("Aceh", 23), ("Jawa Barat", 27)):
        geo, _, _, _ = apply_main_filters(dataset, "2023", prov, "Semua", "Semua", "Semua", "")
        assert set(geo["Provinsi_BPS_Final16E"].unique()) == {prov}
        assert geo["Kabupaten_Kota_BPS_Final16E"].nunique() == expected_kab

    # Verifikasi opsi kabupaten/kota dinamis di AppTest saat memilih Aceh
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[1].set_value("Aceh").run()
    assert not at.exception
    kab_options = at.sidebar.selectbox[2].options
    assert "Kabupaten Aceh Barat Daya" in kab_options
    assert "Kabupaten Bogor" not in kab_options


def test_05_filter_kabupaten_kota(dataset: pd.DataFrame):
    """Skenario 5: Pengujian filter provinsi Aceh -> Kabupaten Aceh Barat Daya."""
    geo, _, _, _ = apply_main_filters(
        dataset, "2023", "Aceh", "Kabupaten Aceh Barat Daya", "Semua", "Semua", ""
    )
    assert len(geo) == 34
    assert set(geo["Kabupaten_Kota_BPS_Final16E"].unique()) == {"Kabupaten Aceh Barat Daya"}


def test_06_filter_kelompok_pangan(dataset: pd.DataFrame):
    """Skenario 6: Pengujian filter kelompok pangan Padi-padian (baris agregat)."""
    _, grp, _, _ = apply_main_filters(
        dataset, "2023", "Semua", "Semua", "Padi-padian", "Semua", ""
    )
    assert len(grp) == 514
    assert grp["_is_agregat"].all()


def test_07_filter_komoditas(dataset: pd.DataFrame):
    """Skenario 7: Pengujian filter komoditas (hanya komoditas penyusun, tanpa agregat)."""
    _, _, cmd, tbl = apply_main_filters(
        dataset, "2023", "Semua", "Semua", "Padi-padian", "Beras", ""
    )
    assert len(cmd) == 514
    assert not cmd["_is_agregat"].any()
    assert not tbl["_is_agregat"].any()


def test_08_pencarian_cepat(dataset: pd.DataFrame):
    """Skenario 8: Pengujian pencarian cepat ('Sleman' dan komoditas 'Beras')."""
    sleman, _, _, _ = apply_main_filters(
        dataset, "Semua", "Semua", "Semua", "Semua", "Semua", "Sleman"
    )
    assert len(sleman) == 102
    assert set(sleman["Kabupaten_Kota_BPS_Final16E"].unique()) == {"Kabupaten Sleman"}

    beras, _, _, _ = apply_main_filters(
        dataset, "Semua", "Semua", "Semua", "Semua", "Semua", "Beras"
    )
    assert len(beras) == 1_542


def test_09_nilai_perlu_tinjauan_sumber(dataset: pd.DataFrame):
    """Skenario 9: Penanganan 8 nilai PERLU_TINJAUAN_SUMBER."""
    review_rows = dataset[dataset["Status_Kelayakan_Dashboard_19"] == STATUS_REVIEW]
    assert len(review_rows) == 8

    chart_default = eligible_chart_rows(dataset, include_review=False)
    chart_included = eligible_chart_rows(dataset, include_review=True)
    assert len(chart_included) - len(chart_default) == 8


def test_10_nilai_tidak_tersedia(dataset: pd.DataFrame):
    """Skenario 10: Penanganan 16 baris TIDAK_TERSEDIA (NaN, bukan 0)."""
    missing_rows = dataset[dataset["Status_Kelayakan_Dashboard_19"] == STATUS_MISSING]
    assert len(missing_rows) == 16
    assert missing_rows["Konsumsi_Pangan_Final"].isna().all()

    chart_included = eligible_chart_rows(dataset, include_review=True)
    assert chart_included["Konsumsi_Pangan_Final"].isna().sum() == 0
    assert len(dataset) - len(chart_included) == 16


def test_11_tabel_data_konsumsi():
    """Skenario 11: Pengujian halaman Tabel Data Konsumsi & kelengkapan 15 kolom audit."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.radio[0].set_value("📋 Tabel Data Konsumsi").run()
    assert not at.exception
    assert len(at.dataframe) >= 1

    df_table = at.dataframe[0].value
    cols = list(df_table.columns)
    assert len(cols) == 15, (
        f"Diharapkan 15 kolom tabel (termasuk Flag Anomali & Catatan Pembersihan Nilai), "
        f"ditemukan {len(cols)} kolom: {cols}"
    )


def test_12_unduh_csv(dataset: pd.DataFrame):
    """Skenario 12: Pengujian unduh CSV (seluruh dataset & filter Jawa Barat 2023 = 918 baris)."""
    _, _, _, tbl_all = apply_main_filters(dataset, "Semua", "Semua", "Semua", "Semua", "Semua", "")
    df_all_csv = pd.read_csv(io.BytesIO(csv_bytes(tbl_all)))
    assert len(df_all_csv) == 52_428

    _, _, _, tbl_jb = apply_main_filters(dataset, "2023", "Jawa Barat", "Semua", "Semua", "Semua", "")
    df_jb_csv = pd.read_csv(io.BytesIO(csv_bytes(tbl_jb)))
    assert len(df_jb_csv) == 918
    assert len(df_jb_csv.columns) == len(tbl_jb.columns)


def test_13_perbandingan_antarwilayah(dataset: pd.DataFrame):
    """Skenario 13: Perbandingan antarwilayah 2023 Kabupaten/Kota Padi-padian."""
    comp_src = eligible_chart_rows(dataset[dataset["Tahun"].eq(2023)], include_review=False)
    comp_padi = comp_src[
        comp_src["_is_agregat"] & comp_src["Kelompok_Bahan_Standar"].eq("Padi-padian")
    ]
    summary = comp_padi.groupby("Kode_Wilayah_BPS_Final16E", as_index=False)["Konsumsi_Pangan_Final"].mean()
    assert len(summary) == 513  # 514 dikurangi 1 nilai PERLU_TINJAUAN_SUMBER
    assert len(summary.nlargest(10, "Konsumsi_Pangan_Final")) == 10
    assert len(summary.nsmallest(10, "Konsumsi_Pangan_Final")) == 10


def test_14_perbandingan_antarperiode(dataset: pd.DataFrame):
    """Skenario 14: Perbandingan tren antarperiode 2021-2023 (487 kab/kota stabil)."""
    id_cols = [
        "Kode_Wilayah_BPS_Final16E",
        "Provinsi_BPS_Final16E",
        "Kabupaten_Kota_BPS_Final16E",
    ]
    identities_by_year = dataset[id_cols + ["Tahun"]].drop_duplicates()
    stable_counts = identities_by_year.groupby(id_cols)["Tahun"].nunique()
    stable_ids = stable_counts[stable_counts.eq(3)].index.tolist()
    assert len(stable_ids) == 487


def test_15_navigasi_halaman():
    """Skenario 15: Pengujian navigasi seluruh 3 halaman via AppTest."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    for page_name in (
        "📊 Dashboard Visualisasi",
        "📋 Tabel Data Konsumsi",
        "ℹ️ Tentang Data & Metodologi",
    ):
        at.sidebar.radio[0].set_value(page_name).run()
        assert not at.exception, f"Error pada halaman {page_name}: {at.exception}"


def test_16_perhitungan_kpi(dataset: pd.DataFrame):
    """Skenario 16: Pengujian perhitungan KPI (tidak mencampur agregat dan komoditas)."""
    # Default: agregat seluruh kelompok
    _, grp_2023, _, _ = apply_main_filters(dataset, "2023", "Semua", "Semua", "Semua", "Semua", "")
    kpi_grp = eligible_chart_rows(grp_2023, include_review=False)
    assert len(kpi_grp) == 4_110  # 4.112 dikurangi 2 anomali agregat 2023
    assert kpi_grp["Provinsi_BPS_Final16E"].nunique() == 38

    # Filter komoditas Beras: hanya komoditas
    _, _, cmd_beras, _ = apply_main_filters(dataset, "2023", "Semua", "Semua", "Padi-padian", "Beras", "")
    kpi_cmd = eligible_chart_rows(cmd_beras, include_review=False)
    assert len(kpi_cmd) == 514
    assert not kpi_cmd["_is_agregat"].any()


def test_17_konsistensi_filter():
    """Skenario 17: Konsistensi filter utama vs kontrol lokal perbandingan di AppTest."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    # Ubah filter utama ke Aceh 2022
    at.sidebar.selectbox[0].set_value("2022").run()
    at.sidebar.selectbox[1].set_value("Aceh").run()
    assert not at.exception
    # Pastikan kontrol lokal perbandingan (compare_year_v2) dan tren (trend_region_v2) tetap ada
    assert any(sb.key == "compare_year_v2" for sb in at.selectbox)
    assert any(sb.key == "trend_region_v2" for sb in at.selectbox)


def test_18_informasi_kualitas_dan_metodologi():
    """Skenario 18: Pengujian halaman Tentang Data & Metodologi via AppTest."""
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.radio[0].set_value("ℹ️ Tentang Data & Metodologi").run()
    assert not at.exception
    all_markdown = "\n".join(m.value for m in at.markdown)
    assert "Badan Pangan Nasional" in all_markdown
    assert "kg / kapita / tahun" in all_markdown
    assert "1.511 baris Nilai Nol" in all_markdown
    assert "16 baris Tidak Tersedia" in all_markdown
    assert "8 baris Anomali Ekstrem" in all_markdown
