"""
Black Box Testing Fungsional Website V3 (READ-ONLY)
Mencakup seluruh 21 skenario BB-01 sampai BB-21 menggunakan pytest & AppTest.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import (
    DATA_FILE,
    STATUS_MISSING,
    STATUS_REVIEW,
    apply_main_filters,
    csv_bytes,
    eligible_chart_rows,
    load_data,
)


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return load_data(str(DATA_FILE))


def test_bb01_pemuatan_aplikasi():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
    assert len(at.sidebar.radio) >= 1
    assert len(at.sidebar.selectbox) >= 5


def test_bb02_navigasi_halaman():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    for page_name in (
        "📊 Dashboard Visualisasi",
        "📋 Tabel Data Konsumsi",
        "ℹ️ Tentang Data & Metodologi",
    ):
        at.sidebar.radio[0].set_value(page_name).run()
        assert not at.exception, f"Error saat membuka {page_name}: {at.exception}"


def test_bb03_filter_tahun(df: pd.DataFrame):
    for yr in ("2021", "2022", "2023"):
        geo, grp, cmd, _ = apply_main_filters(df, yr, "Semua", "Semua", "Semua", "Semua", "")
        assert len(geo) == 17_476
        assert len(grp) == 4_112
        assert len(cmd) == 13_364

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    for yr in ("2021", "2022", "2023"):
        at.sidebar.selectbox[0].set_value(yr).run()
        assert not at.exception


def test_bb04_filter_provinsi(df: pd.DataFrame):
    for prov, expected_kab in (("Aceh", 23), ("Jawa Barat", 27)):
        geo, _, _, _ = apply_main_filters(df, "2023", prov, "Semua", "Semua", "Semua", "")
        assert set(geo["Provinsi_BPS_Final16E"].unique()) == {prov}
        assert geo["Kabupaten_Kota_BPS_Final16E"].nunique() == expected_kab

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[1].set_value("Aceh").run()
    assert not at.exception
    assert "Kabupaten Aceh Barat Daya" in at.sidebar.selectbox[2].options
    assert "Kabupaten Bogor" not in at.sidebar.selectbox[2].options


def test_bb05_filter_kabupaten_kota(df: pd.DataFrame):
    geo, grp, cmd, _ = apply_main_filters(
        df, "2023", "Aceh", "Kabupaten Aceh Barat Daya", "Semua", "Semua", ""
    )
    assert len(geo) == 34
    assert len(grp) == 8
    assert len(cmd) == 26
    assert set(geo["Kabupaten_Kota_BPS_Final16E"].unique()) == {"Kabupaten Aceh Barat Daya"}


def test_bb06_validasi_enam_wilayah_dki_jakarta(df: pd.DataFrame):
    expected_codes = {"3101", "3171", "3172", "3173", "3174", "3175"}
    dki = df[df["Kode_Wilayah_BPS_Final16E"].isin(expected_codes)]
    assert set(dki["Kode_Wilayah_BPS_Final16E"].unique()) == expected_codes

    # Pastikan filter Provinsi="DKI Jakarta" mengembalikan seluruh 6 wilayah termasuk 3175 Jakarta Utara
    geo_dki, _, _, _ = apply_main_filters(df, "2023", "DKI Jakarta", "Semua", "Semua", "Semua", "")
    assert set(geo_dki["Kode_Wilayah_BPS_Final16E"].unique()) == expected_codes

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[1].set_value("DKI Jakarta").run()
    assert not at.exception
    kab_opts = at.sidebar.selectbox[2].options
    # Catat nama aktual di UI untuk 6 wilayah DKI Jakarta
    assert len([k for k in kab_opts if k != "Semua"]) == 6
    assert any("Jakarta Utara" in k for k in kab_opts)


def test_bb07_filter_kelompok_pangan(df: pd.DataFrame):
    _, grp, _, _ = apply_main_filters(df, "2023", "Semua", "Semua", "Padi-padian", "Semua", "")
    assert len(grp) == 514
    assert grp["_is_agregat"].all()


def test_bb08_filter_komoditas(df: pd.DataFrame):
    _, _, cmd, tbl = apply_main_filters(df, "2023", "Semua", "Semua", "Padi-padian", "Beras", "")
    assert len(cmd) == 514
    assert not cmd["_is_agregat"].any()
    assert not tbl["_is_agregat"].any()


def test_bb09_pencarian_cepat(df: pd.DataFrame):
    sleman, _, _, _ = apply_main_filters(df, "Semua", "Semua", "Semua", "Semua", "Semua", "Sleman")
    assert len(sleman) == 102
    assert set(sleman["Kabupaten_Kota_BPS_Final16E"].unique()) == {"Kabupaten Sleman"}

    beras, _, _, _ = apply_main_filters(df, "Semua", "Semua", "Semua", "Semua", "Semua", "Beras")
    assert len(beras) == 1_542


def test_bb10_grafik_kelompok_pangan():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    # Default Semua tahun & Semua wilayah: grafik kelompok pangan harus terbentuk
    assert not at.exception
    # Ubah tahun ke 2023 dan provinsi ke Jawa Barat -> grafik tetap terbentuk tanpa error
    at.sidebar.selectbox[0].set_value("2023").run()
    at.sidebar.selectbox[1].set_value("Jawa Barat").run()
    assert not at.exception


def test_bb11_grafik_komoditas():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[3].set_value("Padi-padian").run()
    at.sidebar.selectbox[4].set_value("Beras").run()
    assert not at.exception


def test_bb12_nilai_tinjauan_sumber(df: pd.DataFrame):
    assert len(df[df["Status_Kelayakan_Dashboard_19"] == STATUS_REVIEW]) == 8
    default_rows = eligible_chart_rows(df, include_review=False)
    included_rows = eligible_chart_rows(df, include_review=True)
    assert len(included_rows) - len(default_rows) == 8

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    assert at.sidebar.checkbox[0].value is False
    at.sidebar.checkbox[0].check().run()
    assert not at.exception


def test_bb13_nilai_tidak_tersedia(df: pd.DataFrame):
    missing = df[df["Status_Kelayakan_Dashboard_19"] == STATUS_MISSING]
    assert len(missing) == 16
    assert missing["Konsumsi_Pangan_Final"].isna().all()
    assert eligible_chart_rows(df, include_review=True)["Konsumsi_Pangan_Final"].isna().sum() == 0


def test_bb14_tabel_data_konsumsi():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.radio[0].set_value("📋 Tabel Data Konsumsi").run()
    assert not at.exception
    cols = list(at.dataframe[0].value.columns)
    assert len(cols) == 15
    for expected in (
        "Konsumsi Final (kg/kapita/tahun)",
        "Nilai Mentah Sumber Asli",
        "Status Kelayakan",
        "Kategori Nilai Data",
        "Flag Anomali Sumber",
        "Catatan Pembersihan Nilai",
        "Penjelasan Audit & Kualitas",
        "Catatan Rekonsiliasi Wilayah",
    ):
        assert expected in cols


def test_bb15_ekspor_csv(df: pd.DataFrame):
    _, _, _, tbl_all = apply_main_filters(df, "Semua", "Semua", "Semua", "Semua", "Semua", "")
    df_all = pd.read_csv(io.BytesIO(csv_bytes(tbl_all)), low_memory=False)
    assert len(df_all) == 52_428

    _, _, _, tbl_jb = apply_main_filters(df, "2023", "Jawa Barat", "Semua", "Semua", "Semua", "")
    df_jb = pd.read_csv(io.BytesIO(csv_bytes(tbl_jb)), low_memory=False)
    assert len(df_jb) == 918


def test_bb16_perbandingan_antarwilayah(df: pd.DataFrame):
    comp_src = eligible_chart_rows(df[df["Tahun"].eq(2023)], include_review=False)
    comp_padi = comp_src[
        comp_src["_is_agregat"] & comp_src["Kelompok_Bahan_Standar"].eq("Padi-padian")
    ]
    summary = comp_padi.groupby("Kode_Wilayah_BPS_Final16E", as_index=False)["Konsumsi_Pangan_Final"].mean()
    assert len(summary) == 513
    assert summary["Kode_Wilayah_BPS_Final16E"].nunique() == 513
    assert len(summary.nlargest(10, "Konsumsi_Pangan_Final")) == 10
    assert len(summary.nsmallest(10, "Konsumsi_Pangan_Final")) == 10


def test_bb17_perbandingan_antarperiode(df: pd.DataFrame):
    id_cols = [
        "Kode_Wilayah_BPS_Final16E",
        "Provinsi_BPS_Final16E",
        "Kabupaten_Kota_BPS_Final16E",
    ]
    counts = df[id_cols + ["Tahun"]].drop_duplicates().groupby(id_cols)["Tahun"].nunique()
    stable = counts[counts.eq(3)]
    assert len(stable) == 487


def test_bb18_ringkasan_kpi(df: pd.DataFrame):
    _, grp_2023, _, _ = apply_main_filters(df, "2023", "Semua", "Semua", "Semua", "Semua", "")
    kpi_grp = eligible_chart_rows(grp_2023, include_review=False)
    assert len(kpi_grp) == 4_110
    assert kpi_grp["Provinsi_BPS_Final16E"].nunique() == 38

    _, _, cmd_beras, _ = apply_main_filters(df, "2023", "Semua", "Semua", "Padi-padian", "Beras", "")
    kpi_cmd = eligible_chart_rows(cmd_beras, include_review=False)
    assert len(kpi_cmd) == 514
    assert not kpi_cmd["_is_agregat"].any()


def test_bb19_konsistensi_filter():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.selectbox[0].set_value("2022").run()
    at.sidebar.selectbox[1].set_value("Aceh").run()
    assert not at.exception
    assert any(sb.key == "compare_year_v2" for sb in at.selectbox)
    assert any(sb.key == "trend_region_v2" for sb in at.selectbox)


def test_bb20_informasi_metodologi_kualitas():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.radio[0].set_value("ℹ️ Tentang Data & Metodologi").run()
    assert not at.exception
    md = "\n".join(m.value for m in at.markdown)
    assert "Badan Pangan Nasional" in md
    assert "kg / kapita / tahun" in md
    assert "1.511 baris Nilai Nol" in md
    assert "16 baris Tidak Tersedia" in md
    assert "8 baris Anomali Ekstrem" in md


def test_bb21_penanganan_kondisi_tanpa_hasil(df: pd.DataFrame):
    geo, grp, cmd, tbl = apply_main_filters(
        df, "Semua", "Semua", "Semua", "Semua", "Semua", "KATA_KUNCI_TIDAK_ADA_XYZ"
    )
    assert geo.empty and grp.empty and cmd.empty and tbl.empty

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=30)
    at.run()
    at.sidebar.text_input[0].set_value("KATA_KUNCI_TIDAK_ADA_XYZ").run()
    assert not at.exception
    infos = [i.value for i in at.info]
    assert any("Tidak ada nilai agregat kelompok pangan" in msg for msg in infos)
    assert any("Tidak ada nilai komoditas" in msg for msg in infos)

    # Pulihkan filter ke kosong -> aplikasi kembali normal
    at.sidebar.text_input[0].set_value("").run()
    assert not at.exception

