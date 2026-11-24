
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# =====================================================
# 1. KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(
    page_title="Visualisasi Konsumsi Pangan",
    page_icon="🍚",
    layout="wide"
)

DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "Dataset_Bapanas_Referensi_Wilayah_BPS.csv"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.15);
    }

    div[data-testid="stMetricValue"] {
        font-size: 25px;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# 2. MEMBACA DAN MEMPERSIAPKAN DATA
# =====================================================

@st.cache_data
def load_data(file_path):

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    kolom_wajib = [
        "Tahun",
        "Kode Wilayah",
        "Provinsi_BPS_Standar",
        "Kabupaten_Kota_BPS_Standar",
        "Kelompok_Bahan_Standar",
        "Komoditas_Standar",
        "Konsumsi_Pangan_Analisis"
    ]

    kolom_hilang = [
        kolom for kolom in kolom_wajib
        if kolom not in data.columns
    ]

    if kolom_hilang:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {kolom_hilang}"
        )

    data["Tahun"] = pd.to_numeric(
        data["Tahun"],
        errors="coerce"
    ).astype("Int64")

    nilai = (
        data["Konsumsi_Pangan_Analisis"]
        .astype("string")
        .str.strip()
        .str.replace(",", ".", regex=False)
    )

    data["Konsumsi_Pangan_Analisis"] = pd.to_numeric(
        nilai,
        errors="coerce"
    )

    kolom_teks = {
        "_provinsi": "Provinsi_BPS_Standar",
        "_kabupaten": "Kabupaten_Kota_BPS_Standar",
        "_kelompok": "Kelompok_Bahan_Standar",
        "_komoditas": "Komoditas_Standar"
    }

    for kolom_baru, kolom_asal in kolom_teks.items():

        data[kolom_baru] = (
            data[kolom_asal]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Membedakan data agregat dengan komoditas penyusun

    kelompok_norm = data["_kelompok"].str.casefold()
    komoditas_norm = data["_komoditas"].str.casefold()

    data["_is_agregat"] = (
        kelompok_norm.ne("")
        & kelompok_norm.eq(komoditas_norm)
    )

    return data


if not DATA_FILE.exists():

    st.error(
        "Dataset tidak ditemukan. "
        "Periksa kembali file di dalam folder data."
    )

    st.stop()


try:

    df = load_data(str(DATA_FILE))

except Exception as error:

    st.error(f"Dataset gagal dibaca: {error}")

    st.stop()


# =====================================================
# 3. FUNGSI PENDUKUNG
# =====================================================

def format_angka(nilai, desimal=2):

    if pd.isna(nilai):
        return "-"

    return (
        f"{nilai:,.{desimal}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def ambil_opsi(data, kolom):

    nilai = (
        data[kolom]
        .dropna()
        .astype(str)
        .str.strip()
    )

    nilai = sorted([
        item for item in nilai.unique().tolist()
        if item != ""
    ])

    return ["Semua"] + nilai


def periksa_pilihan(key, opsi):

    if st.session_state.get(key, "Semua") not in opsi:

        st.session_state[key] = "Semua"


def buat_csv(data):

    return data.to_csv(
        index=False
    ).encode("utf-8-sig")


def siapkan_indikator_perbandingan(
    data,
    pilihan_tahun,
    pilihan_kelompok,
    pilihan_komoditas
):

    hasil = data.copy()

    # Filter tahun

    if pilihan_tahun != "Semua":

        hasil = hasil[
            hasil["Tahun"] == int(pilihan_tahun)
        ]

    # Filter kelompok pangan

    if pilihan_kelompok != "Semua":

        hasil = hasil[
            hasil["_kelompok"] == pilihan_kelompok
        ]

    # Menentukan sumber data indikator

    if pilihan_komoditas != "Semua":

        hasil = hasil[
            (~hasil["_is_agregat"])
            & (hasil["_komoditas"] == pilihan_komoditas)
        ]

    elif pilihan_kelompok != "Semua":

        hasil = hasil[
            hasil["_is_agregat"]
        ]

    else:

        return pd.DataFrame()

    hasil = hasil.dropna(
        subset=[
            "Tahun",
            "Kode Wilayah",
            "Konsumsi_Pangan_Analisis"
        ]
    )

    return hasil


def hitung_perbandingan(data, tingkat):

    if tingkat == "Provinsi":

        kolom_wilayah = ["_provinsi"]

        per_tahun = (
            data.groupby(
                kolom_wilayah + ["Tahun"],
                as_index=False
            )["Konsumsi_Pangan_Analisis"]
            .mean()
        )

        hasil = (
            per_tahun.groupby(
                "_provinsi",
                as_index=False
            )["Konsumsi_Pangan_Analisis"]
            .mean()
        )

        hasil = hasil.rename(
            columns={
                "_provinsi": "Wilayah",
                "Konsumsi_Pangan_Analisis": "Rata-rata Konsumsi"
            }
        )

    else:

        kolom_wilayah = [
            "Kode Wilayah",
            "_provinsi",
            "_kabupaten"
        ]

        per_tahun = (
            data.groupby(
                kolom_wilayah + ["Tahun"],
                as_index=False
            )["Konsumsi_Pangan_Analisis"]
            .mean()
        )

        hasil = (
            per_tahun.groupby(
                kolom_wilayah,
                as_index=False
            )["Konsumsi_Pangan_Analisis"]
            .mean()
        )

        hasil["Wilayah"] = (
            hasil["_kabupaten"]
            + " ("
            + hasil["_provinsi"]
            + ")"
        )

        hasil = hasil.rename(
            columns={
                "Konsumsi_Pangan_Analisis": "Rata-rata Konsumsi"
            }
        )

    return hasil


# =====================================================
# 4. SIDEBAR NAVIGASI
# =====================================================

st.sidebar.title("🍚 Konsumsi Pangan")

st.sidebar.caption(
    "Sistem Informasi Visualisasi Konsumsi "
    "Pangan Kabupaten/Kota Indonesia"
)

halaman = st.sidebar.radio(
    "Navigasi",
    [
        "Dashboard",
        "Data Konsumsi",
        "Tentang Sistem"
    ],
    key="menu_navigasi"
)

st.sidebar.divider()

st.sidebar.caption("Periode data: 2021–2023")
st.sidebar.caption("Sumber: Badan Pangan Nasional")


# =====================================================
# 5. JUDUL SISTEM
# =====================================================

st.title("Sistem Informasi Visualisasi Konsumsi Pangan")

st.caption(
    "Visualisasi data konsumsi pangan kabupaten/kota "
    "Indonesia periode 2021–2023."
)

st.divider()


# =====================================================
# 6. FILTER UTAMA
# =====================================================

st.subheader("Filter Data Konsumsi Pangan")

df_filter = df.copy()

tahun = sorted(
    df["Tahun"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

filter1, filter2, filter3, filter4, filter5 = st.columns(5)


# FILTER TAHUN

opsi_tahun = ["Semua"] + [
    str(item) for item in tahun
]

periksa_pilihan("pilih_tahun", opsi_tahun)

with filter1:

    pilihan_tahun = st.selectbox(
        "Tahun",
        opsi_tahun,
        key="pilih_tahun"
    )

if pilihan_tahun != "Semua":

    df_filter = df_filter[
        df_filter["Tahun"] == int(pilihan_tahun)
    ]


# FILTER PROVINSI

opsi_provinsi = ambil_opsi(
    df_filter,
    "_provinsi"
)

periksa_pilihan("pilih_provinsi", opsi_provinsi)

with filter2:

    pilihan_provinsi = st.selectbox(
        "Provinsi",
        opsi_provinsi,
        key="pilih_provinsi"
    )

if pilihan_provinsi != "Semua":

    df_filter = df_filter[
        df_filter["_provinsi"] == pilihan_provinsi
    ]


# FILTER KABUPATEN/KOTA

opsi_kabupaten = ambil_opsi(
    df_filter,
    "_kabupaten"
)

periksa_pilihan("pilih_kabupaten", opsi_kabupaten)

with filter3:

    pilihan_kabupaten = st.selectbox(
        "Kabupaten/Kota",
        opsi_kabupaten,
        key="pilih_kabupaten"
    )

if pilihan_kabupaten != "Semua":

    df_filter = df_filter[
        df_filter["_kabupaten"] == pilihan_kabupaten
    ]


# FILTER KELOMPOK PANGAN

opsi_kelompok = ambil_opsi(
    df_filter,
    "_kelompok"
)

periksa_pilihan("pilih_kelompok", opsi_kelompok)

with filter4:

    pilihan_kelompok = st.selectbox(
        "Kelompok Pangan",
        opsi_kelompok,
        key="pilih_kelompok"
    )

if pilihan_kelompok != "Semua":

    df_filter = df_filter[
        df_filter["_kelompok"] == pilihan_kelompok
    ]


# MENYIMPAN DATA SEBELUM FILTER KOMODITAS

df_scope_kelompok = df_filter.copy()


# FILTER KOMODITAS

df_opsi_komoditas = df_filter[
    ~df_filter["_is_agregat"]
]

opsi_komoditas = ambil_opsi(
    df_opsi_komoditas,
    "_komoditas"
)

periksa_pilihan("pilih_komoditas", opsi_komoditas)

with filter5:

    pilihan_komoditas = st.selectbox(
        "Komoditas",
        opsi_komoditas,
        key="pilih_komoditas"
    )

if pilihan_komoditas != "Semua":

    df_filter = df_filter[
        (~df_filter["_is_agregat"])
        & (df_filter["_komoditas"] == pilihan_komoditas)
    ]


st.caption(
    f"Jumlah data setelah penyaringan: "
    f"{len(df_filter):,} baris".replace(",", ".")
)

st.divider()


# =====================================================
# 7. MENENTUKAN INDIKATOR UTAMA
# =====================================================

if pilihan_komoditas != "Semua":

    df_indikator = df_filter[
        ~df_filter["_is_agregat"]
    ].copy()

    nama_indikator = f"Komoditas: {pilihan_komoditas}"

elif pilihan_kelompok != "Semua":

    df_indikator = df_scope_kelompok[
        df_scope_kelompok["_is_agregat"]
    ].copy()

    nama_indikator = f"Kelompok pangan: {pilihan_kelompok}"

else:

    df_indikator = df_scope_kelompok[
        df_scope_kelompok["_is_agregat"]
    ].copy()

    nama_indikator = "Seluruh kelompok pangan"

df_indikator = df_indikator.dropna(
    subset=["Konsumsi_Pangan_Analisis"]
)


# =====================================================
# 8. HALAMAN DASHBOARD
# =====================================================

if halaman == "Dashboard":

    st.header("Dashboard Konsumsi Pangan")

    st.caption(
        "Ringkasan dan visualisasi konsumsi pangan "
        "berdasarkan data yang telah difilter."
    )

    # -------------------------------------------------
    # KPI
    # -------------------------------------------------

    st.subheader("Ringkasan Informasi")

    rata_konsumsi = (
        df_indikator["Konsumsi_Pangan_Analisis"].mean()
        if not df_indikator.empty
        else float("nan")
    )

    jumlah_provinsi = (
        df_indikator["_provinsi"].nunique()
        if not df_indikator.empty
        else 0
    )

    jumlah_wilayah = (
        df_indikator["Kode Wilayah"].nunique()
        if not df_indikator.empty
        else 0
    )

    jumlah_komoditas = (
        1 if pilihan_komoditas != "Semua"
        else df_scope_kelompok[
            ~df_scope_kelompok["_is_agregat"]
        ]["_komoditas"].nunique()
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Rata-rata Konsumsi",
        format_angka(rata_konsumsi)
    )

    k2.metric(
        "Jumlah Provinsi",
        f"{jumlah_provinsi:,}".replace(",", ".")
    )

    k3.metric(
        "Jumlah Kabupaten/Kota",
        f"{jumlah_wilayah:,}".replace(",", ".")
    )

    k4.metric(
        "Jumlah Komoditas",
        f"{jumlah_komoditas:,}".replace(",", ".")
    )

    st.caption(
        f"Indikator ringkasan: {nama_indikator}. "
        "Rata-rata merupakan rata-rata aritmetika "
        "atas observasi yang memenuhi filter."
    )

    st.divider()


    # =================================================
    # 8A. VISUALISASI KELOMPOK PANGAN
    # =================================================

    st.subheader(
        "1. Visualisasi Konsumsi Berdasarkan Kelompok Pangan"
    )

    st.caption(
        "Grafik menggunakan data agregat kelompok pangan."
    )

    df_agregat = df_scope_kelompok[
        df_scope_kelompok["_is_agregat"]
    ].copy()

    df_agregat = df_agregat.dropna(
        subset=["Tahun", "Konsumsi_Pangan_Analisis"]
    )

    if df_agregat.empty:

        st.info(
            "Data agregat kelompok pangan tidak tersedia."
        )

    else:

        ringkasan_kelompok = (
            df_agregat
            .groupby(
                ["Tahun", "_kelompok"],
                as_index=False
            )["Konsumsi_Pangan_Analisis"]
            .mean()
        )

        ringkasan_kelompok = ringkasan_kelompok.rename(
            columns={
                "_kelompok": "Kelompok Pangan",
                "Konsumsi_Pangan_Analisis": "Rata-rata Konsumsi"
            }
        )

        if (
            pilihan_tahun == "Semua"
            and ringkasan_kelompok["Tahun"].nunique() > 1
        ):

            fig_kelompok = px.line(
                ringkasan_kelompok,
                x="Tahun",
                y="Rata-rata Konsumsi",
                color="Kelompok Pangan",
                markers=True,
                title="Tren Konsumsi per Kelompok Pangan",
                template="plotly_dark"
            )

            fig_kelompok.update_xaxes(
                tickmode="linear",
                dtick=1
            )

        else:

            fig_kelompok = px.bar(
                ringkasan_kelompok,
                x="Kelompok Pangan",
                y="Rata-rata Konsumsi",
                color="Kelompok Pangan",
                title="Rata-rata Konsumsi per Kelompok Pangan",
                template="plotly_dark"
            )

            fig_kelompok.update_layout(
                showlegend=False
            )

        fig_kelompok.update_layout(
            height=450,
            xaxis_title=(
                "Tahun" if pilihan_tahun == "Semua"
                else "Kelompok Pangan"
            ),
            yaxis_title="Konsumsi (kg/kapita/tahun)"
        )

        st.plotly_chart(
            fig_kelompok,
            use_container_width=True,
            key="grafik_kelompok"
        )

        st.caption(
            "Nilai merupakan rata-rata aritmetika antarwilayah "
            "dalam cakupan filter, bukan total konsumsi nasional."
        )

    st.divider()


    # =================================================
    # 8B. VISUALISASI KOMODITAS
    # =================================================

    st.subheader(
        "2. Visualisasi Konsumsi Berdasarkan Komoditas"
    )

    df_komoditas = df_filter[
        ~df_filter["_is_agregat"]
    ].copy()

    df_komoditas = df_komoditas.dropna(
        subset=["Konsumsi_Pangan_Analisis"]
    )

    if df_komoditas.empty:

        st.info(
            "Data komoditas tidak tersedia untuk filter ini."
        )

    else:

        if (
            pilihan_komoditas != "Semua"
            and pilihan_tahun == "Semua"
            and df_komoditas["Tahun"].nunique() > 1
        ):

            ringkasan_komoditas = (
                df_komoditas
                .groupby(
                    ["Tahun", "_komoditas"],
                    as_index=False
                )["Konsumsi_Pangan_Analisis"]
                .mean()
            )

            ringkasan_komoditas = ringkasan_komoditas.rename(
                columns={
                    "_komoditas": "Komoditas",
                    "Konsumsi_Pangan_Analisis": "Rata-rata Konsumsi"
                }
            )

            fig_komoditas = px.line(
                ringkasan_komoditas,
                x="Tahun",
                y="Rata-rata Konsumsi",
                markers=True,
                title=f"Tren Konsumsi {pilihan_komoditas}",
                template="plotly_dark"
            )

            fig_komoditas.update_xaxes(
                tickmode="linear",
                dtick=1
            )

        else:

            ringkasan_komoditas = (
                df_komoditas
                .groupby(
                    ["_kelompok", "_komoditas"],
                    as_index=False
                )["Konsumsi_Pangan_Analisis"]
                .mean()
            )

            ringkasan_komoditas = ringkasan_komoditas.rename(
                columns={
                    "_kelompok": "Kelompok Pangan",
                    "_komoditas": "Komoditas",
                    "Konsumsi_Pangan_Analisis": "Rata-rata Konsumsi"
                }
            )

            ringkasan_komoditas = (
                ringkasan_komoditas
                .nlargest(
                    10,
                    "Rata-rata Konsumsi"
                )
                .sort_values(
                    "Rata-rata Konsumsi",
                    ascending=True
                )
            )

            judul_komoditas = (
                f"Rata-rata Konsumsi Komoditas {pilihan_komoditas}"
                if pilihan_komoditas != "Semua"
                else "10 Komoditas dengan Konsumsi Tertinggi"
            )

            fig_komoditas = px.bar(
                ringkasan_komoditas,
                x="Rata-rata Konsumsi",
                y="Komoditas",
                color="Kelompok Pangan",
                orientation="h",
                title=judul_komoditas,
                template="plotly_dark"
            )

        fig_komoditas.update_layout(
            height=450,
            xaxis_title="Konsumsi (kg/kapita/tahun)",
            yaxis_title="Komoditas"
        )

        st.plotly_chart(
            fig_komoditas,
            use_container_width=True,
            key="grafik_komoditas"
        )

        st.caption(
            "Grafik menggunakan data komoditas dan "
            "tidak mencampurkannya dengan data agregat."
        )

    st.divider()


    # =================================================
    # 8C. PERBANDINGAN ANTARWILAYAH
    # =================================================

    st.subheader(
        "3. Perbandingan Konsumsi Antarwilayah"
    )

    st.caption(
        "Bagian ini menggunakan cakupan perbandingan "
        "tersendiri sehingga filter geografis utama "
        "tidak membatasi seluruh wilayah yang dibandingkan."
    )

    # Menyiapkan indikator dari dataset penuh.
    # Filter tahun, kelompok, dan komoditas tetap berlaku.
    # Filter provinsi dan kabupaten/kota utama tidak diterapkan.

    df_perbandingan = siapkan_indikator_perbandingan(
        df,
        pilihan_tahun,
        pilihan_kelompok,
        pilihan_komoditas
    )

    if df_perbandingan.empty:

        st.info(
            "Pilih satu kelompok pangan atau satu komoditas "
            "pada filter utama untuk memulai perbandingan wilayah."
        )

    else:

        st.caption(
            f"Indikator perbandingan: "
            f"{pilihan_komoditas if pilihan_komoditas != 'Semua' else pilihan_kelompok}"
        )

        tingkat_wilayah = st.radio(
            "Tingkat Perbandingan",
            [
                "Provinsi",
                "Kabupaten/Kota"
            ],
            horizontal=True,
            key="tingkat_perbandingan_v4"
        )

        data_scope = df_perbandingan.copy()

        # Cakupan seluruh provinsi

        if tingkat_wilayah == "Provinsi":

            st.caption(
                "Menampilkan perbandingan provinsi "
                "di seluruh Indonesia."
            )

        # Cakupan kabupaten/kota

        else:

            pilihan_cakupan = st.radio(
                "Cakupan Wilayah",
                [
                    "Seluruh Indonesia",
                    "Dalam Satu Provinsi"
                ],
                horizontal=True,
                key="cakupan_kabupaten_v4"
            )

            if pilihan_cakupan == "Dalam Satu Provinsi":

                daftar_provinsi = sorted(
                    data_scope["_provinsi"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                if daftar_provinsi:

                    provinsi_perbandingan = st.selectbox(
                        "Pilih Provinsi untuk Perbandingan",
                        daftar_provinsi,
                        key="provinsi_perbandingan_v4"
                    )

                    data_scope = data_scope[
                        data_scope["_provinsi"] == provinsi_perbandingan
                    ]

            else:

                st.caption(
                    "Menampilkan perbandingan kabupaten/kota "
                    "di seluruh Indonesia."
                )

        # Menghitung hasil perbandingan

        ringkasan_wilayah = hitung_perbandingan(
            data_scope,
            tingkat_wilayah
        )

        if ringkasan_wilayah.empty:

            st.warning(
                "Data perbandingan wilayah tidak tersedia."
            )

        else:

            st.caption(
                f"Jumlah wilayah yang dapat dibandingkan: "
                f"{len(ringkasan_wilayah)}"
            )

            atas = (
                ringkasan_wilayah
                .nlargest(
                    10,
                    "Rata-rata Konsumsi"
                )
                .sort_values(
                    "Rata-rata Konsumsi",
                    ascending=True
                )
            )

            bawah = (
                ringkasan_wilayah
                .nsmallest(
                    10,
                    "Rata-rata Konsumsi"
                )
                .sort_values(
                    "Rata-rata Konsumsi",
                    ascending=True
                )
            )

            col1, col2 = st.columns(2)

            # GRAFIK TERTINGGI

            with col1:

                st.markdown(
                    "**10 Wilayah dengan Konsumsi Tertinggi**"
                )

                fig_atas = px.bar(
                    atas,
                    x="Rata-rata Konsumsi",
                    y="Wilayah",
                    orientation="h",
                    title="Peringkat Tertinggi",
                    template="plotly_dark",
                    hover_data={
                        "Rata-rata Konsumsi": ":.2f"
                    }
                )

                fig_atas.update_layout(
                    height=480,
                    xaxis_title="Konsumsi (kg/kapita/tahun)",
                    yaxis_title="Wilayah"
                )

                st.plotly_chart(
                    fig_atas,
                    use_container_width=True,
                    key="grafik_wilayah_tertinggi_v4"
                )

            # GRAFIK TERENDAH

            with col2:

                st.markdown(
                    "**10 Wilayah dengan Konsumsi Terendah**"
                )

                fig_bawah = px.bar(
                    bawah,
                    x="Rata-rata Konsumsi",
                    y="Wilayah",
                    orientation="h",
                    title="Peringkat Terendah",
                    template="plotly_dark",
                    hover_data={
                        "Rata-rata Konsumsi": ":.2f"
                    }
                )

                fig_bawah.update_layout(
                    height=480,
                    xaxis_title="Konsumsi (kg/kapita/tahun)",
                    yaxis_title="Wilayah"
                )

                st.plotly_chart(
                    fig_bawah,
                    use_container_width=True,
                    key="grafik_wilayah_terendah_v4"
                )

            st.caption(
                "Hasil perbandingan dihitung berdasarkan "
                "rata-rata nilai konsumsi pada periode "
                "dan indikator yang dipilih."
            )

            with st.expander(
                "Lihat tabel hasil perbandingan wilayah"
            ):

                tabel_perbandingan = (
                    ringkasan_wilayah
                    .sort_values(
                        "Rata-rata Konsumsi",
                        ascending=False
                    )
                    .copy()
                )

                tabel_perbandingan[
                    "Rata-rata Konsumsi"
                ] = tabel_perbandingan[
                    "Rata-rata Konsumsi"
                ].round(4)

                st.dataframe(
                    tabel_perbandingan,
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "Unduh Hasil Perbandingan (CSV)",
                    data=buat_csv(tabel_perbandingan),
                    file_name="hasil_perbandingan_wilayah.csv",
                    mime="text/csv",
                    key="unduh_perbandingan_v4"
                )


# =====================================================
# 9. HALAMAN DATA KONSUMSI
# =====================================================

elif halaman == "Data Konsumsi":

    st.header("Data Konsumsi Pangan")

    st.caption(
        "Menampilkan data berdasarkan kombinasi filter "
        "yang telah dipilih."
    )

    kolom_tampil = [
        "Tahun",
        "Kode Wilayah",
        "Provinsi_BPS_Standar",
        "Kabupaten_Kota_BPS_Standar",
        "Kelompok_Bahan_Standar",
        "Komoditas_Standar",
        "Konsumsi_Pangan_Analisis"
    ]

    data_tampil = df_filter[kolom_tampil].copy()

    col1, col2 = st.columns(2)

    col1.metric(
        "Jumlah Data Terpilih",
        f"{len(data_tampil):,}".replace(",", ".")
    )

    col2.metric(
        "Jumlah Wilayah",
        f"{data_tampil['Kode Wilayah'].nunique():,}"
        .replace(",", ".")
    )

    st.dataframe(
        data_tampil.head(100),
        use_container_width=True,
        hide_index=True
    )

    if len(data_tampil) > 100:

        st.caption(
            "Pratinjau menampilkan maksimal 100 baris pertama. "
            "Unduh CSV untuk memperoleh seluruh hasil penyaringan."
        )

    st.download_button(
        label="⬇️ Unduh Data Hasil Filter (CSV)",
        data=buat_csv(data_tampil),
        file_name="data_konsumsi_pangan_filter.csv",
        mime="text/csv",
        use_container_width=True,
        key="unduh_data_konsumsi_v4"
    )


# =====================================================
# 10. HALAMAN TENTANG SISTEM
# =====================================================

elif halaman == "Tentang Sistem":

    st.header("Tentang Sistem")

    st.markdown("""
    Sistem Informasi Visualisasi Konsumsi Pangan
    Kabupaten/Kota Indonesia merupakan aplikasi berbasis web
    yang menyajikan informasi konsumsi pangan melalui
    visualisasi data interaktif.

    Sistem ini menggunakan data dari Badan Pangan Nasional
    dengan periode pengamatan 2021–2023.
    """)

    st.subheader("Tujuan Sistem")

    st.markdown("""
    - Mempermudah pengguna memperoleh informasi konsumsi pangan.
    - Menyajikan perbandingan konsumsi berdasarkan wilayah.
    - Menampilkan tren konsumsi berdasarkan tahun.
    - Mempermudah penelusuran data melalui fitur filter.
    - Menyediakan fasilitas unduh data untuk analisis.
    """)

    st.subheader("Metode Pengembangan")

    st.markdown("""
    Pengembangan sistem menggunakan metode
    **User-Centered Design (UCD)** yang berorientasi
    pada kebutuhan dan pengalaman pengguna.

    Pengembangan memperhatikan identifikasi kebutuhan pengguna,
    perancangan solusi, evaluasi, dan penyempurnaan sistem.
    """)

    st.subheader("Teknologi yang Digunakan")

    st.markdown("""
    - Python: bahasa pemrograman.
    - Streamlit: pengembangan aplikasi berbasis web.
    - Pandas: pengolahan dan pengelolaan data.
    - Plotly Express: pembuatan visualisasi interaktif.
    """)

    st.subheader("Sumber Data")

    st.write(
        "Badan Pangan Nasional (2024). "
        "Rata-rata Konsumsi per Jenis Pangan Penduduk "
        "Indonesia Kabupaten/Kota Tahun 2021–2023."
    )

    st.caption(
        "Informasi sistem disesuaikan dengan "
        "implementasi aktual penelitian."
    )


# =====================================================
# 11. INFORMASI BAGIAN BAWAH
# =====================================================

st.divider()

st.caption(
    "Sumber data: Badan Pangan Nasional (2024) | "
    "Periode 2021–2023"
)

st.caption(
    "Sistem Informasi Visualisasi Konsumsi Pangan "
    "Kabupaten/Kota Indonesia"
)