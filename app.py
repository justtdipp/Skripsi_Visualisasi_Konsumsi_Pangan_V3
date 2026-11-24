from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# SISTEM INFORMASI VISUALISASI KONSUMSI PANGAN
# Dataset: Bapanas 2021-2023, hasil finalisasi V2
# ============================================================

st.set_page_config(
    page_title="Visualisasi Konsumsi Pangan",
    page_icon="🍚",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = (
    BASE_DIR
    / "data"
    / "final"
    / "19_Dataset_Bapanas_Siap_Analisis_2021_2023_KOREKSI_SUMBER_V2.csv"
)

# Status default yang boleh masuk ke grafik. Status dengan catatan tetap
# ditampilkan, tetapi diberi penjelasan. Status anomali tinggi dikecualikan
# secara default; nilai tidak tersedia tidak akan dihitung sebagai nol.
STATUS_ELIGIBLE = {
    "DAPAT_DIGUNAKAN",
    "DAPAT_DIGUNAKAN_DENGAN_CATATAN",
}
STATUS_REVIEW = "PERLU_TINJAUAN_SUMBER"
STATUS_MISSING = "TIDAK_TERSEDIA"

REQUIRED_COLUMNS = [
    "No",
    "Tahun",
    "Kode Wilayah",
    "Provinsi",
    "Kabupaten_Kota",
    "Kelompok Bahan",
    "Komoditas",
    "Konsumsi Pangan",
    "Kode_Wilayah_BPS_Final16E",
    "Kode_Provinsi_BPS_Final16E",
    "Provinsi_BPS_Final16E",
    "Kabupaten_Kota_BPS_Final16E",
    "Tipe_Wilayah_BPS_Final16E",
    "Kelompok_Bahan_Standar",
    "Komoditas_Standar",
    "Konsumsi_Pangan_Final",
    "Status_Final_Dataset_19",
    "Status_Kelayakan_Dashboard_19",
    "Catatan_Final_Dataset_19",
]

TEXT_COLUMNS = [
    "Kode Wilayah",
    "Provinsi",
    "Kabupaten_Kota",
    "Kelompok Bahan",
    "Komoditas",
    "Konsumsi Pangan",
    "Kode_Wilayah_BPS_Final16E",
    "Kode_Provinsi_BPS_Final16E",
    "Provinsi_BPS_Final16E",
    "Kabupaten_Kota_BPS_Final16E",
    "Tipe_Wilayah_BPS_Final16E",
    "Kelompok_Bahan_Standar",
    "Komoditas_Standar",
    "Status_Final_Dataset_19",
    "Status_Kelayakan_Dashboard_19",
    "Catatan_Final_Dataset_19",
]


@st.cache_data(show_spinner="Memuat dataset konsumsi pangan...")
def load_data(path: str) -> pd.DataFrame:
    """Muat dan validasi dataset V2 tanpa mengubah file sumber."""
    frame = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(
            "Kolom wajib tidak ditemukan pada CSV V2: " + ", ".join(missing)
        )

    if len(frame) != 52_428:
        raise ValueError(
            f"Jumlah baris CSV V2 tidak sesuai. Diharapkan 52.428, "
            f"ditemukan {len(frame):,}. Pastikan file yang digunakan adalah "
            "dataset final V2, bukan dataset crosswalk tahap validasi."
        )

    frame["Tahun"] = pd.to_numeric(frame["Tahun"], errors="coerce").astype("Int64")
    frame["Konsumsi_Pangan_Final"] = pd.to_numeric(
        frame["Konsumsi_Pangan_Final"], errors="coerce"
    )

    for col in TEXT_COLUMNS:
        frame[col] = frame[col].fillna("").astype(str).str.strip()

    # Agregat kelompok pangan dikenali dari kesamaan label kelompok dan komoditas.
    group_norm = frame["Kelompok_Bahan_Standar"].str.casefold()
    commodity_norm = frame["Komoditas_Standar"].str.casefold()
    frame["_is_agregat"] = group_norm.ne("") & group_norm.eq(commodity_norm)

    # Kunci wilayah-tahun disimpan untuk pemeriksaan dan pengelompokan.
    frame["_region_year_key"] = (
        frame["Tahun"].astype("string")
        + "|"
        + frame["Kode_Wilayah_BPS_Final16E"].astype("string")
    )

    # Pemeriksaan struktur data yang sudah dikonfirmasi pada CSV V2.
    years = set(frame["Tahun"].dropna().astype(int).tolist())
    if years != {2021, 2022, 2023}:
        raise ValueError(f"Periode data tidak sesuai: {sorted(years)}")

    region_counts = (
        frame.groupby("Tahun")["Kode_Wilayah_BPS_Final16E"].nunique().to_dict()
    )
    if any(region_counts.get(y) != 514 for y in (2021, 2022, 2023)):
        raise ValueError(
            "Struktur wilayah tidak sesuai dengan validasi CSV V2: "
            f"{region_counts}"
        )

    # Validasi tambahan agar aplikasi tidak diam-diam membaca CSV lama/keliru.
    expected_quality = {
        "DAPAT_DIGUNAKAN": 52_393,
        "DAPAT_DIGUNAKAN_DENGAN_CATATAN": 11,
        "PERLU_TINJAUAN_SUMBER": 8,
        "TIDAK_TERSEDIA": 16,
    }
    actual_quality = frame["Status_Kelayakan_Dashboard_19"].value_counts().to_dict()
    if actual_quality != expected_quality:
        raise ValueError(
            "Distribusi status kualitas tidak sesuai dengan dataset final V2. "
            f"Diharapkan {expected_quality}, ditemukan {actual_quality}."
        )

    if frame["Kode_Wilayah_BPS_Final16E"].isna().any():
        raise ValueError("Ditemukan kode wilayah BPS kosong pada dataset final V2.")

    duplicate_key = frame.duplicated(
        [
            "Tahun",
            "Kode_Wilayah_BPS_Final16E",
            "Kelompok_Bahan_Standar",
            "Komoditas_Standar",
        ]
    )
    if duplicate_key.any():
        raise ValueError(
            f"Ditemukan {int(duplicate_key.sum())} duplikasi kunci indikator-wilayah-tahun."
        )

    if frame["Konsumsi_Pangan_Final"].lt(0).any():
        raise ValueError("Ditemukan nilai konsumsi final negatif yang tidak diharapkan.")

    aggregate_count = int(frame["_is_agregat"].sum())
    if aggregate_count != 12_336:
        raise ValueError(
            "Jumlah baris agregat kelompok pangan tidak sesuai. "
            f"Diharapkan 12.336, ditemukan {aggregate_count:,}."
        )

    return frame


def format_num(value: float | int | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_int(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def sorted_options(series: pd.Series) -> list[str]:
    values = {
        str(value).strip()
        for value in series.dropna().tolist()
        if str(value).strip()
    }
    return sorted(values, key=lambda value: value.casefold())


def with_all(values: Iterable[str]) -> list[str]:
    return ["Semua"] + list(values)


def csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8-sig")


def eligible_chart_rows(frame: pd.DataFrame, include_review: bool) -> pd.DataFrame:
    allowed = set(STATUS_ELIGIBLE)
    if include_review:
        allowed.add(STATUS_REVIEW)
    return frame.loc[
        frame["Status_Kelayakan_Dashboard_19"].isin(allowed)
        & frame["Konsumsi_Pangan_Final"].notna()
    ].copy()


def average_by_region_year(frame: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    """Rata-ratakan observasi per wilayah-tahun sebelum ringkasan lanjutan."""
    if frame.empty:
        return pd.DataFrame(columns=group_columns + ["Rata-rata Konsumsi"])
    return (
        frame.groupby(group_columns, as_index=False, dropna=False)["Konsumsi_Pangan_Final"]
        .mean()
        .rename(columns={"Konsumsi_Pangan_Final": "Rata-rata Konsumsi"})
    )


def apply_main_filters(
    frame: pd.DataFrame,
    year_choice: str,
    province_choice: str,
    district_choice: str,
    group_choice: str,
    commodity_choice: str,
    search_query: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Kembalikan data umum, data agregat kelompok, data komoditas, dan tabel."""
    geo = frame.copy()

    if year_choice != "Semua":
        geo = geo.loc[geo["Tahun"].eq(int(year_choice))]
    if province_choice != "Semua":
        geo = geo.loc[geo["Provinsi_BPS_Final16E"].eq(province_choice)]
    if district_choice != "Semua":
        geo = geo.loc[geo["Kabupaten_Kota_BPS_Final16E"].eq(district_choice)]

    if search_query.strip():
        term = search_query.strip().casefold()
        search_columns = [
            "Provinsi_BPS_Final16E",
            "Kabupaten_Kota_BPS_Final16E",
            "Kelompok_Bahan_Standar",
            "Komoditas_Standar",
        ]
        mask = pd.Series(False, index=geo.index)
        for col in search_columns:
            mask |= geo[col].str.casefold().str.contains(term, regex=False, na=False)
        geo = geo.loc[mask]

    group_scope = geo.copy()
    if group_choice != "Semua":
        group_scope = group_scope.loc[
            group_scope["Kelompok_Bahan_Standar"].eq(group_choice)
        ]

    group_rows = group_scope.loc[group_scope["_is_agregat"]].copy()
    commodity_rows = group_scope.loc[~group_scope["_is_agregat"]].copy()
    if commodity_choice != "Semua":
        commodity_rows = commodity_rows.loc[
            commodity_rows["Komoditas_Standar"].eq(commodity_choice)
        ]

    # Tabel memuat semua status kualitas untuk transparansi; pengguna dapat menyaringnya.
    table_rows = group_scope.copy()
    if commodity_choice != "Semua":
        table_rows = table_rows.loc[
            (~table_rows["_is_agregat"])
            & table_rows["Komoditas_Standar"].eq(commodity_choice)
        ]

    return geo, group_rows, commodity_rows, table_rows


# ============================================================
# LOAD DATA
# ============================================================
if not DATA_FILE.exists():
    st.error(
        "Dataset V2 tidak ditemukan. Letakkan file CSV di folder data/ "
        "dengan nama persis sesuai petunjuk README."
    )
    st.stop()

try:
    df = load_data(str(DATA_FILE))
except Exception as exc:  # tampilkan alasan teknis tanpa menghentikan traceback ke pengguna
    st.error(f"Dataset gagal dimuat: {exc}")
    st.stop()

# Ringkasan kualitas yang berasal dari kolom status dataset final.
quality_counts = (
    df["Status_Kelayakan_Dashboard_19"].value_counts().to_dict()
)
count_usable = int(quality_counts.get("DAPAT_DIGUNAKAN", 0))
count_notes = int(quality_counts.get("DAPAT_DIGUNAKAN_DENGAN_CATATAN", 0))
count_review = int(quality_counts.get(STATUS_REVIEW, 0))
count_missing = int(quality_counts.get(STATUS_MISSING, 0))


# ============================================================
# SIDEBAR / NAVIGASI / FILTER
# ============================================================
st.sidebar.title("🍚 Konsumsi Pangan")
st.sidebar.caption("Sistem Informasi Visualisasi Konsumsi Pangan Kabupaten/Kota Indonesia")
page = st.sidebar.radio(
    "Navigasi",
    ["Dashboard", "Data Konsumsi", "Tentang Data"],
    key="main_navigation_v2",
)
st.sidebar.divider()
st.sidebar.markdown("**Filter data**")

all_years = sorted(df["Tahun"].dropna().astype(int).unique().tolist())
year_options = with_all([str(year) for year in all_years])
year_choice = st.sidebar.selectbox("Tahun", year_options, index=0)

geo_for_filters = df.copy()
if year_choice != "Semua":
    geo_for_filters = geo_for_filters.loc[
        geo_for_filters["Tahun"].eq(int(year_choice))
    ]

province_options = with_all(sorted_options(geo_for_filters["Provinsi_BPS_Final16E"]))
province_choice = st.sidebar.selectbox("Provinsi", province_options, index=0)

if province_choice != "Semua":
    geo_for_filters = geo_for_filters.loc[
        geo_for_filters["Provinsi_BPS_Final16E"].eq(province_choice)
    ]

district_options = with_all(sorted_options(geo_for_filters["Kabupaten_Kota_BPS_Final16E"]))
district_choice = st.sidebar.selectbox("Kabupaten/Kota", district_options, index=0)

group_options = with_all(sorted_options(df["Kelompok_Bahan_Standar"]))
group_choice = st.sidebar.selectbox("Kelompok pangan", group_options, index=0)

commodity_pool = df.loc[~df["_is_agregat"]].copy()
if group_choice != "Semua":
    commodity_pool = commodity_pool.loc[
        commodity_pool["Kelompok_Bahan_Standar"].eq(group_choice)
    ]
commodity_options = with_all(sorted_options(commodity_pool["Komoditas_Standar"]))
commodity_choice = st.sidebar.selectbox("Komoditas", commodity_options, index=0)

search_query = st.sidebar.text_input(
    "Pencarian cepat",
    placeholder="Cari wilayah atau komoditas...",
    help="Pencarian mencakup provinsi, kabupaten/kota, kelompok pangan, dan komoditas.",
)

include_review = st.sidebar.checkbox(
    "Sertakan 8 nilai yang perlu tinjauan sumber",
    value=False,
    help="Jika diaktifkan, nilai yang ditandai PERLU_TINJAUAN_SUMBER dapat ikut masuk grafik. Secara default nilai tersebut dikecualikan.",
)

geo_filtered, group_rows_all, commodity_rows_all, table_rows_all = apply_main_filters(
    df,
    year_choice,
    province_choice,
    district_choice,
    group_choice,
    commodity_choice,
    search_query,
)
chart_geo = eligible_chart_rows(geo_filtered, include_review)
chart_group = eligible_chart_rows(group_rows_all, include_review)
chart_commodity = eligible_chart_rows(commodity_rows_all, include_review)

st.sidebar.divider()
st.sidebar.caption("Periode data: 2021–2023")
st.sidebar.caption("Sumber: Badan Pangan Nasional (2024)")


# ============================================================
# HEADER GLOBAL
# ============================================================
st.title("Sistem Informasi Visualisasi Konsumsi Pangan")
st.caption(
    "Visualisasi data konsumsi pangan penduduk kabupaten/kota Indonesia "
    "periode 2021–2023. Satuan: kg/kapita/tahun."
)

if count_notes:
    st.info(
        f"Dataset memuat {format_int(count_notes)} nilai hasil rekonsiliasi/koreksi "
        "yang ditandai DAPAT_DIGUNAKAN_DENGAN_CATATAN. Nilai tersebut disertakan "
        "dengan catatan transparansi."
    )
if not include_review and count_review:
    st.caption(
        f"Secara default {format_int(count_review)} nilai berstatus perlu tinjauan "
        "sumber tidak dimasukkan ke grafik. Aktifkan opsinya di sidebar untuk meninjaunya."
    )


# ============================================================
# PAGE 1 — DASHBOARD
# ============================================================
if page == "Dashboard":
    st.header("Dashboard Konsumsi Pangan")
    st.caption("Ringkasan dan grafik diperbarui mengikuti filter di panel kiri.")

    # Pilih indikator KPI yang tidak mencampurkan agregat kelompok dan komoditas.
    if commodity_choice != "Semua":
        kpi_source = chart_commodity
        kpi_label = f"Komoditas: {commodity_choice}"
    elif group_choice != "Semua":
        kpi_source = chart_group
        kpi_label = f"Agregat kelompok: {group_choice}"
    else:
        kpi_source = chart_group
        kpi_label = "Rata-rata observasi agregat seluruh kelompok"

    avg_value = (
        float(kpi_source["Konsumsi_Pangan_Final"].mean())
        if not kpi_source.empty else np.nan
    )
    observed_rows = len(kpi_source)
    provinces_count = kpi_source["Provinsi_BPS_Final16E"].nunique() if observed_rows else 0
    regions_per_year = (
        kpi_source.groupby("Tahun")["Kode_Wilayah_BPS_Final16E"].nunique()
        if observed_rows else pd.Series(dtype=int)
    )
    average_regions = float(regions_per_year.mean()) if not regions_per_year.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rata-rata nilai konsumsi", format_num(avg_value), help="Rata-rata aritmetika atas observasi sesuai indikator dan filter; bukan total konsumsi nasional.")
    c2.metric("Provinsi tercakup", format_int(provinces_count))
    c3.metric("Cakupan wilayah per tahun", format_num(average_regions, 0))
    c4.metric("Observasi indikator", format_int(observed_rows))
    st.caption(
        f"Indikator KPI: {kpi_label}. Nilai merupakan rata-rata observasi "
        "dalam satuan kg/kapita/tahun, bukan penjumlahan konsumsi nasional."
    )
    st.divider()

    # Grafik agregat kelompok pangan: hanya 8 baris agregat per wilayah-tahun.
    st.subheader("1. Konsumsi berdasarkan kelompok pangan")
    if chart_group.empty:
        st.info("Tidak ada nilai agregat kelompok pangan untuk kombinasi filter ini.")
    else:
        group_summary = (
            chart_group.groupby(["Tahun", "Kelompok_Bahan_Standar"], as_index=False)
            ["Konsumsi_Pangan_Final"].mean()
            .rename(columns={
                "Kelompok_Bahan_Standar": "Kelompok pangan",
                "Konsumsi_Pangan_Final": "Rata-rata konsumsi",
            })
        )
        if year_choice == "Semua" and group_summary["Tahun"].nunique() > 1:
            fig_group = px.line(
                group_summary,
                x="Tahun",
                y="Rata-rata konsumsi",
                color="Kelompok pangan",
                markers=True,
                title="Tren rata-rata konsumsi per kelompok pangan",
                template="plotly_white",
            )
            fig_group.update_xaxes(tickmode="linear", dtick=1)
        else:
            fig_group = px.bar(
                group_summary,
                x="Kelompok pangan",
                y="Rata-rata konsumsi",
                color="Kelompok pangan",
                title="Rata-rata konsumsi per kelompok pangan",
                template="plotly_white",
            )
            fig_group.update_layout(showlegend=False)
        fig_group.update_layout(
            height=430,
            xaxis_title="Tahun" if year_choice == "Semua" else "Kelompok pangan",
            yaxis_title="Konsumsi (kg/kapita/tahun)",
            margin=dict(l=20, r=20, t=60, b=40),
        )
        st.plotly_chart(fig_group, use_container_width=True)
        st.caption(
            "Grafik ini memakai baris agregat kelompok pangan. Nilainya tidak "
            "dijumlahkan kembali dengan komoditas penyusunnya."
        )
    st.divider()

    # Grafik komoditas: baris komoditas, bukan baris agregat kelompok.
    st.subheader("2. Konsumsi berdasarkan komoditas")
    if chart_commodity.empty:
        st.info("Tidak ada nilai komoditas untuk kombinasi filter ini.")
    elif commodity_choice != "Semua" and year_choice == "Semua":
        commodity_trend = (
            chart_commodity.groupby("Tahun", as_index=False)["Konsumsi_Pangan_Final"]
            .mean()
            .rename(columns={"Konsumsi_Pangan_Final": "Rata-rata konsumsi"})
        )
        fig_commodity = px.line(
            commodity_trend,
            x="Tahun",
            y="Rata-rata konsumsi",
            markers=True,
            title=f"Tren konsumsi komoditas: {commodity_choice}",
            template="plotly_white",
        )
        fig_commodity.update_xaxes(tickmode="linear", dtick=1)
        fig_commodity.update_layout(
            height=420,
            yaxis_title="Konsumsi (kg/kapita/tahun)",
            margin=dict(l=20, r=20, t=60, b=40),
        )
        st.plotly_chart(fig_commodity, use_container_width=True)
    else:
        commodity_summary = (
            chart_commodity.groupby(
                ["Kelompok_Bahan_Standar", "Komoditas_Standar"],
                as_index=False,
            )["Konsumsi_Pangan_Final"]
            .mean()
            .rename(columns={
                "Kelompok_Bahan_Standar": "Kelompok pangan",
                "Komoditas_Standar": "Komoditas",
                "Konsumsi_Pangan_Final": "Rata-rata konsumsi",
            })
        )
        commodity_summary = commodity_summary.nlargest(10, "Rata-rata konsumsi")
        fig_commodity = px.bar(
            commodity_summary.sort_values("Rata-rata konsumsi"),
            x="Rata-rata konsumsi",
            y="Komoditas",
            color="Kelompok pangan",
            orientation="h",
            title="10 komoditas dengan rata-rata konsumsi tertinggi pada filter aktif",
            template="plotly_white",
        )
        fig_commodity.update_layout(
            height=460,
            xaxis_title="Konsumsi (kg/kapita/tahun)",
            yaxis_title="Komoditas",
            margin=dict(l=20, r=20, t=60, b=40),
        )
        st.plotly_chart(fig_commodity, use_container_width=True)
    st.caption(
        "Grafik komoditas menggunakan baris komoditas penyusun. Baris agregat "
        "kelompok pangan dipisahkan agar tidak terjadi penghitungan ganda."
    )
    st.divider()

    # Perbandingan wilayah dalam satu tahun dan satu indikator.
    st.subheader("3. Perbandingan konsumsi antarwilayah")
    st.caption(
        "Pilih satu tahun dan satu indikator agar wilayah dibandingkan pada "
        "periode dan satuan yang sama."
    )
    cmp1, cmp2, cmp3 = st.columns(3)
    compare_year_options = [str(y) for y in all_years]
    default_compare_year = "2023" if "2023" in compare_year_options else compare_year_options[-1]
    with cmp1:
        compare_year = st.selectbox(
            "Tahun perbandingan",
            compare_year_options,
            index=compare_year_options.index(
                year_choice if year_choice != "Semua" else default_compare_year
            ),
            key="compare_year_v2",
        )
    with cmp2:
        compare_level = st.selectbox(
            "Tingkat wilayah",
            ["Kabupaten/Kota", "Provinsi"],
            key="compare_level_v2",
        )
    with cmp3:
        compare_kind = st.selectbox(
            "Jenis indikator",
            ["Kelompok pangan", "Komoditas"],
            key="compare_kind_v2",
        )

    compare_source = eligible_chart_rows(df, include_review)
    compare_source = compare_source.loc[compare_source["Tahun"].eq(int(compare_year))]

    if compare_kind == "Kelompok pangan":
        compare_groups = sorted_options(
            compare_source.loc[compare_source["_is_agregat"], "Kelompok_Bahan_Standar"]
        )
        selected_compare_group = st.selectbox(
            "Pilih kelompok pangan",
            compare_groups,
            key="compare_group_v2",
        )
        comparison = compare_source.loc[
            compare_source["_is_agregat"]
            & compare_source["Kelompok_Bahan_Standar"].eq(selected_compare_group)
        ].copy()
        indicator_text = selected_compare_group
    else:
        compare_groups = sorted_options(
            compare_source.loc[~compare_source["_is_agregat"], "Kelompok_Bahan_Standar"]
        )
        selected_compare_group = st.selectbox(
            "Pilih kelompok pangan",
            compare_groups,
            key="compare_commodity_group_v2",
        )
        possible_commodities = sorted_options(
            compare_source.loc[
                (~compare_source["_is_agregat"])
                & compare_source["Kelompok_Bahan_Standar"].eq(selected_compare_group),
                "Komoditas_Standar",
            ]
        )
        selected_compare_commodity = st.selectbox(
            "Pilih komoditas",
            possible_commodities,
            key="compare_commodity_v2",
        )
        comparison = compare_source.loc[
            (~compare_source["_is_agregat"])
            & compare_source["Kelompok_Bahan_Standar"].eq(selected_compare_group)
            & compare_source["Komoditas_Standar"].eq(selected_compare_commodity)
        ].copy()
        indicator_text = selected_compare_commodity

    if comparison.empty:
        st.info("Data indikator perbandingan tidak tersedia.")
    else:
        if compare_level == "Provinsi":
            comparison_summary = (
                comparison.groupby("Provinsi_BPS_Final16E", as_index=False)
                ["Konsumsi_Pangan_Final"].mean()
                .rename(columns={
                    "Provinsi_BPS_Final16E": "Wilayah",
                    "Konsumsi_Pangan_Final": "Rata-rata konsumsi",
                })
            )
        else:
            comparison_summary = (
                comparison.groupby(
                    [
                        "Kode_Wilayah_BPS_Final16E",
                        "Provinsi_BPS_Final16E",
                        "Kabupaten_Kota_BPS_Final16E",
                    ],
                    as_index=False,
                )["Konsumsi_Pangan_Final"]
                .mean()
                .rename(columns={
                    "Konsumsi_Pangan_Final": "Rata-rata konsumsi",
                })
            )
            comparison_summary["Wilayah"] = (
                comparison_summary["Kabupaten_Kota_BPS_Final16E"]
                + " (" + comparison_summary["Provinsi_BPS_Final16E"] + ")"
            )

        st.caption(
            f"Indikator: {indicator_text} | Tahun: {compare_year} | "
            f"Jumlah wilayah dibandingkan: {format_int(len(comparison_summary))}"
        )
        if compare_level == "Provinsi":
            st.caption(
                "Catatan: nilai provinsi pada grafik merupakan rata-rata sederhana "
                "observasi kabupaten/kota di provinsi tersebut, bukan total konsumsi "
                "provinsi dan bukan rata-rata berbobot jumlah penduduk."
            )
        top10 = comparison_summary.nlargest(10, "Rata-rata konsumsi").sort_values("Rata-rata konsumsi")
        bottom10 = comparison_summary.nsmallest(10, "Rata-rata konsumsi").sort_values("Rata-rata konsumsi")
        left, right = st.columns(2)
        with left:
            fig_top = px.bar(
                top10,
                x="Rata-rata konsumsi",
                y="Wilayah",
                orientation="h",
                title="10 wilayah dengan nilai tertinggi",
                template="plotly_white",
            )
            fig_top.update_layout(height=470, xaxis_title="kg/kapita/tahun", yaxis_title="")
            st.plotly_chart(fig_top, use_container_width=True)
        with right:
            fig_bottom = px.bar(
                bottom10,
                x="Rata-rata konsumsi",
                y="Wilayah",
                orientation="h",
                title="10 wilayah dengan nilai terendah",
                template="plotly_white",
            )
            fig_bottom.update_layout(height=470, xaxis_title="kg/kapita/tahun", yaxis_title="")
            st.plotly_chart(fig_bottom, use_container_width=True)

        with st.expander("Lihat tabel lengkap hasil perbandingan"):
            st.dataframe(
                comparison_summary.sort_values("Rata-rata konsumsi", ascending=False),
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Unduh hasil perbandingan (CSV)",
                csv_bytes(comparison_summary),
                file_name=f"perbandingan_{compare_year}_{compare_kind.lower().replace('/', '-')}.csv",
                mime="text/csv",
            )
    st.divider()

    # Perbandingan antarperiode untuk identitas wilayah yang sama pada semua tahun.
    st.subheader("4. Perbandingan antarperiode pada wilayah yang sama")
    st.caption(
        "Tren ini hanya ditawarkan untuk identitas kode, provinsi, dan nama wilayah "
        "yang tersedia secara konsisten pada ketiga tahun. Wilayah yang berubah "
        "akibat pemekaran atau perubahan identitas dapat tidak masuk daftar ini."
    )

    identity_cols = [
        "Kode_Wilayah_BPS_Final16E",
        "Provinsi_BPS_Final16E",
        "Kabupaten_Kota_BPS_Final16E",
    ]
    identities_by_year = df[identity_cols + ["Tahun"]].drop_duplicates()
    stable_identity_counts = identities_by_year.groupby(identity_cols)["Tahun"].nunique()
    stable_identities = stable_identity_counts[stable_identity_counts.eq(3)].index.tolist()

    if stable_identities:
        stable_options = []
        stable_lookup = {}
        for code, province, district in stable_identities:
            label = f"{district} — {province} ({code})"
            stable_options.append(label)
            stable_lookup[label] = (code, province, district)
        stable_options = sorted(stable_options, key=lambda x: x.casefold())

        trend_region = st.selectbox(
            "Pilih wilayah untuk melihat tren 2021–2023",
            stable_options,
            key="trend_region_v2",
        )
        tr1, tr2 = st.columns(2)
        trend_type = tr1.selectbox(
            "Indikator tren",
            ["Kelompok pangan", "Komoditas"],
            key="trend_type_v2",
        )
        trend_groups = sorted_options(df["Kelompok_Bahan_Standar"])
        trend_group = tr2.selectbox(
            "Kelompok pangan untuk tren",
            trend_groups,
            key="trend_group_v2",
        )
        trend_frame = eligible_chart_rows(df, include_review)
        code, province, district = stable_lookup[trend_region]
        trend_frame = trend_frame.loc[
            trend_frame["Kode_Wilayah_BPS_Final16E"].eq(code)
            & trend_frame["Provinsi_BPS_Final16E"].eq(province)
            & trend_frame["Kabupaten_Kota_BPS_Final16E"].eq(district)
        ]
        if trend_type == "Kelompok pangan":
            trend_frame = trend_frame.loc[
                trend_frame["_is_agregat"]
                & trend_frame["Kelompok_Bahan_Standar"].eq(trend_group)
            ]
            trend_value_label = trend_group
        else:
            trend_commodities = sorted_options(
                trend_frame.loc[
                    (~trend_frame["_is_agregat"])
                    & trend_frame["Kelompok_Bahan_Standar"].eq(trend_group),
                    "Komoditas_Standar",
                ]
            )
            if trend_commodities:
                trend_commodity = st.selectbox(
                    "Komoditas untuk tren",
                    trend_commodities,
                    key="trend_commodity_v2",
                )
                trend_frame = trend_frame.loc[
                    (~trend_frame["_is_agregat"])
                    & trend_frame["Kelompok_Bahan_Standar"].eq(trend_group)
                    & trend_frame["Komoditas_Standar"].eq(trend_commodity)
                ]
                trend_value_label = trend_commodity
            else:
                trend_value_label = "Komoditas tidak tersedia"

        if trend_frame["Tahun"].nunique() >= 2:
            trend_summary = (
                trend_frame.groupby("Tahun", as_index=False)["Konsumsi_Pangan_Final"]
                .mean()
                .rename(columns={"Konsumsi_Pangan_Final": "Konsumsi"})
            )
            fig_trend = px.line(
                trend_summary,
                x="Tahun",
                y="Konsumsi",
                markers=True,
                title=f"Tren {trend_value_label} — {district}",
                template="plotly_white",
            )
            fig_trend.update_xaxes(tickmode="linear", dtick=1)
            fig_trend.update_layout(
                height=390,
                xaxis_title="Tahun",
                yaxis_title="Konsumsi (kg/kapita/tahun)",
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info(
                "Data indikator ini tidak tersedia pada minimal dua tahun "
                "untuk identitas wilayah yang sama."
            )
    else:
        st.info("Belum ditemukan identitas wilayah yang konsisten pada ketiga tahun.")


# ============================================================
# PAGE 2 — DATA KONSUMSI
# ============================================================
elif page == "Data Konsumsi":
    st.header("Data Konsumsi Pangan")
    st.caption(
        "Tabel menampilkan data sesuai filter. Status kualitas disediakan agar "
        "pengguna dapat membedakan nilai tersedia, nilai dengan catatan, anomali, "
        "dan nilai yang tidak tersedia."
    )

    status_options = [
        "DAPAT_DIGUNAKAN",
        "DAPAT_DIGUNAKAN_DENGAN_CATATAN",
        "PERLU_TINJAUAN_SUMBER",
        "TIDAK_TERSEDIA",
    ]
    selected_statuses = st.multiselect(
        "Status kualitas data",
        status_options,
        default=status_options,
        help="Secara default semua status ditampilkan pada tabel. Status ini tidak mengubah file CSV.",
    )
    table_view = table_rows_all.loc[
        table_rows_all["Status_Kelayakan_Dashboard_19"].isin(selected_statuses)
    ].copy()

    t1, t2, t3 = st.columns(3)
    t1.metric("Baris sesuai filter", format_int(len(table_view)))
    t2.metric(
        "Perlu tinjauan sumber",
        format_int(int(table_view["Status_Kelayakan_Dashboard_19"].eq(STATUS_REVIEW).sum())),
    )
    t3.metric(
        "Tidak tersedia",
        format_int(int(table_view["Status_Kelayakan_Dashboard_19"].eq(STATUS_MISSING).sum())),
    )

    display_columns = [
        "No",
        "Tahun",
        "Kode_Wilayah_BPS_Final16E",
        "Provinsi_BPS_Final16E",
        "Kabupaten_Kota_BPS_Final16E",
        "Kelompok_Bahan_Standar",
        "Komoditas_Standar",
        "Konsumsi_Pangan_Final",
        "Status_Kelayakan_Dashboard_19",
        "Status_Final_Dataset_19",
        "Flag_Anomali_Sumber_19",
        "Catatan_Final_Dataset_19",
        "Catatan_Pembersihan_Nilai_18",
        "Catatan_Rekonsiliasi_16E",
        "Konsumsi Pangan",
    ]
    display_columns = [col for col in display_columns if col in table_view.columns]
    table_view = table_view[display_columns].copy()
    table_view = table_view.rename(columns={
        "Kode_Wilayah_BPS_Final16E": "Kode BPS",
        "Provinsi_BPS_Final16E": "Provinsi",
        "Kabupaten_Kota_BPS_Final16E": "Kabupaten/Kota",
        "Kelompok_Bahan_Standar": "Kelompok pangan",
        "Komoditas_Standar": "Komoditas",
        "Konsumsi_Pangan_Final": "Konsumsi final (kg/kapita/tahun)",
        "Status_Kelayakan_Dashboard_19": "Status kelayakan dashboard",
        "Status_Final_Dataset_19": "Status nilai final",
        "Flag_Anomali_Sumber_19": "Flag anomali sumber",
        "Catatan_Final_Dataset_19": "Catatan finalisasi",
        "Catatan_Pembersihan_Nilai_18": "Catatan pembersihan nilai",
        "Catatan_Rekonsiliasi_16E": "Catatan rekonsiliasi wilayah",
        "Konsumsi Pangan": "Nilai sumber asli",
    })

    st.dataframe(
        table_view.head(300),
        use_container_width=True,
        hide_index=True,
    )
    if len(table_view) > 300:
        st.caption(
            f"Pratinjau menampilkan 300 dari {format_int(len(table_view))} baris. "
            "Gunakan tombol unduh untuk memperoleh seluruh hasil filter."
        )
    st.download_button(
        "Unduh seluruh data sesuai filter (CSV)",
        csv_bytes(table_view),
        file_name="data_konsumsi_pangan_hasil_filter.csv",
        mime="text/csv",
    )


# ============================================================
# PAGE 3 — TENTANG DATA
# ============================================================
else:
    st.header("Tentang Sistem dan Kualitas Data")
    st.markdown(
        "Sistem ini menyajikan informasi konsumsi pangan penduduk pada tingkat "
        "kabupaten/kota di Indonesia untuk membantu pengguna menelusuri, memahami, "
        "dan membandingkan data melalui filter, grafik, dan tabel."
    )

    st.subheader("Sumber dan cakupan data")
    st.write(
        "Sumber konsumsi: Badan Pangan Nasional (2024), *Rata-rata Konsumsi per "
        "Jenis Pangan Penduduk Indonesia Kabupaten/Kota Tahun 2021–2023*."
    )
    st.write("Periode: 2021–2023. Satuan: kg per kapita per tahun.")

    coverage = (
        df.groupby("Tahun")
        .agg(
            Baris=("No", "count"),
            Wilayah=("Kode_Wilayah_BPS_Final16E", "nunique"),
            Provinsi=("Provinsi_BPS_Final16E", "nunique"),
        )
        .reset_index()
    )
    st.dataframe(coverage, use_container_width=True, hide_index=True)
    st.caption(
        "Struktur provinsi pada referensi kerja: 34 provinsi pada 2021 dan 2022, "
        "serta 38 provinsi pada 2023. Karena ada perubahan wilayah administratif, "
        "perbandingan antarperiode perlu memperhatikan konsistensi identitas wilayah."
    )
    st.warning(
        "Identitas kode dan nama wilayah pada aplikasi merupakan hasil standardisasi, "
        "pemetaan, dan rekonsiliasi dalam pengolahan data penelitian. Hasil tersebut "
        "tidak boleh ditafsirkan sebagai pengesahan atau konfirmasi resmi dari BPS. "
        "Catatan keputusan pemetaan dan kasus yang memerlukan penjelasan tetap perlu "
        "dirujuk pada arsip audit penelitian."
    )

    st.subheader("Status kualitas dataset")
    zero_count = int(df["Status_Final_Dataset_19"].eq("NILAI_NOL_SUMBER").sum())
    empty_count = int(df["Status_Kelayakan_Dashboard_19"].eq(STATUS_MISSING).sum())
    anomaly_count = int(df["Status_Kelayakan_Dashboard_19"].eq(STATUS_REVIEW).sum())
    q1, q2, q3 = st.columns(3)
    q1.metric("Nilai nol dari sumber", format_int(zero_count))
    q2.metric("Nilai tidak tersedia", format_int(empty_count))
    q3.metric("Nilai perlu tinjauan", format_int(anomaly_count))
    quality_table = pd.DataFrame(
        [
            ["DAPAT_DIGUNAKAN", count_usable, "Nilai tersedia dan lolos pemeriksaan dasar."],
            ["DAPAT_DIGUNAKAN_DENGAN_CATATAN", count_notes, "Nilai hasil rekonsiliasi/koreksi yang disertai catatan."],
            ["PERLU_TINJAUAN_SUMBER", count_review, "Nilai ekstrem dari sumber; dikecualikan dari grafik secara default."],
            ["TIDAK_TERSEDIA", count_missing, "Nilai tidak tersedia di sumber; tidak diperlakukan sebagai nol."],
        ],
        columns=["Status", "Jumlah baris", "Perlakuan di sistem"],
    )
    st.dataframe(quality_table, use_container_width=True, hide_index=True)

    st.warning(
        "Delapan nilai yang ditandai PERLU_TINJAUAN_SUMBER tetap dipertahankan "
        "untuk ketertelusuran, tetapi tidak dimasukkan ke grafik secara default. "
        "Enam belas nilai TIDAK_TERSEDIA ditampilkan sebagai data tidak tersedia, "
        "bukan sebagai nilai nol."
    )
    st.info(
        "Sebelas baris berstatus DAPAT_DIGUNAKAN_DENGAN_CATATAN mencakup nilai "
        "hasil rekonsiliasi dan koreksi. Catatan pengolahannya tersedia pada "
        "dataset dan halaman Data Konsumsi."
    )

    st.subheader("Keterangan penghitungan")
    st.markdown(
        "- Grafik kelompok pangan menggunakan baris agregat kelompok pangan.\n"
        "- Grafik komoditas menggunakan baris komoditas penyusun.\n"
        "- Rata-rata yang ditampilkan adalah rata-rata aritmetika observasi yang "
        "memenuhi filter, bukan total konsumsi nasional.\n"
        "- Baris agregat kelompok tidak dijumlahkan kembali dengan komoditas "
        "penyusunnya untuk menghindari penghitungan ganda."
    )

    st.subheader("Teknologi")
    st.write("Python, Streamlit, Pandas, dan Plotly.")

st.divider()
st.caption(
    "Sumber konsumsi: Badan Pangan Nasional (2024) | Periode 2021–2023 | "
    "Satuan: kg/kapita/tahun | Dataset kerja: hasil finalisasi V2 peneliti."
)
