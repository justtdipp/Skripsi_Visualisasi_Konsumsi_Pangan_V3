"""
Pengujian Integritas Dataset Final V2 (READ-ONLY)
Tidak mengubah, mengisi, atau menulis ulang dataset sumber.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import DATA_FILE, STATUS_MISSING, STATUS_REVIEW, load_data


def test_dataset_file_exists_and_readonly_load():
    assert DATA_FILE.exists(), f"Dataset V2 tidak ditemukan: {DATA_FILE}"
    assert DATA_FILE.name == "19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv"

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        raw = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
    assert raw.shape == (52_428, 35), f"Dimensi tidak sesuai: {raw.shape}"
    # low_memory=False seharusnya mencegah DtypeWarning; catat jika ada
    dtype_warnings = [w for w in caught if issubclass(w.category, pd.errors.DtypeWarning)]
    assert len(dtype_warnings) == 0


def test_dataset_structure_and_years():
    df = load_data(str(DATA_FILE))
    assert len(df) == 52_428
    assert set(df["Tahun"].dropna().astype(int).unique()) == {2021, 2022, 2023}

    counts_per_year = df.groupby("Tahun").size().to_dict()
    assert counts_per_year == {2021: 17_476, 2022: 17_476, 2023: 17_476}

    regions_per_year = df.groupby("Tahun")["Kode_Wilayah_BPS_Final16E"].nunique().to_dict()
    assert regions_per_year == {2021: 514, 2022: 514, 2023: 514}


def test_dataset_keys_and_types():
    df = load_data(str(DATA_FILE))
    dup = df.duplicated([
        "Tahun",
        "Kode_Wilayah_BPS_Final16E",
        "Kelompok_Bahan_Standar",
        "Komoditas_Standar",
    ])
    assert int(dup.sum()) == 0
    assert df["Kode_Wilayah_BPS_Final16E"].eq("").sum() == 0
    assert df["Provinsi_BPS_Final16E"].eq("").sum() == 0
    assert df["Kabupaten_Kota_BPS_Final16E"].eq("").sum() == 0
    assert df["Kelompok_Bahan_Standar"].eq("").sum() == 0
    assert df["Komoditas_Standar"].eq("").sum() == 0

    assert pd.api.types.is_integer_dtype(df["Tahun"])
    assert pd.api.types.is_float_dtype(df["Konsumsi_Pangan_Final"])
    assert not df["Konsumsi_Pangan_Final"].lt(0).any()


def test_dataset_quality_categories():
    df = load_data(str(DATA_FILE))
    quality = df["Status_Kelayakan_Dashboard_19"].value_counts().to_dict()
    assert quality == {
        "DAPAT_DIGUNAKAN": 52_393,
        "DAPAT_DIGUNAKAN_DENGAN_CATATAN": 11,
        "PERLU_TINJAUAN_SUMBER": 8,
        "TIDAK_TERSEDIA": 16,
    }

    zero_count = int(df["Status_Final_Dataset_19"].eq("NILAI_NOL_SUMBER").sum())
    assert zero_count == 1_511

    missing_rows = df[df["Status_Kelayakan_Dashboard_19"] == STATUS_MISSING]
    assert len(missing_rows) == 16
    assert missing_rows["Konsumsi_Pangan_Final"].isna().all()

    review_rows = df[df["Status_Kelayakan_Dashboard_19"] == STATUS_REVIEW]
    assert len(review_rows) == 8
    assert review_rows["Konsumsi_Pangan_Final"].notna().all()

    notes_rows = df[df["Status_Kelayakan_Dashboard_19"] == "DAPAT_DIGUNAKAN_DENGAN_CATATAN"]
    assert len(notes_rows) == 11
    assert notes_rows["Catatan_Final_Dataset_19"].ne("").all()

