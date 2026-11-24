from __future__ import annotations

import re
import sys
import time
import unicodedata
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import requests

YEARS = [2021, 2022, 2023]
BASE_API = "https://sipedas.pertanian.go.id/api/wilayah/list_wilayah"
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "hasil_validasi"
DEFAULT_FILENAME = "Dataset_Bapanas_Referensi_Wilayah_BPS.csv"

# Variasi ejaan yang diketahui dari pemeriksaan dataset.
# Alias hanya menyamakan penulisan nama; tidak mengganti nilai konsumsi.
DISTRICT_ALIASES = {
    "BIREUEM": "BIREUEN",
    "LABUAN BATU": "LABUHANBATU",
    "MANDALING NATAL": "MANDAILING NATAL",
    "PAMEKSAAN": "PAMEKASAN",
    "SIMEULEU": "SIMEULUE",
    "BIAK NAMFOR": "BIAK NUMFOR",
    "WAY KAWAN": "WAY KANAN",
    "PRABUMILIH": "PRABUMULIH",
    "SAWAH LUNTO": "SAWAHLUNTO",
    "TANJUNG BALAI": "TANJUNGBALAI",
    "PADANG SIDIMPUAN": "PADANGSIDIMPUAN",
    "PANGKAL PINANG": "PANGKALPINANG",
    "TOBA SAMOSIR": "TOBA",
    "MALUKU TENGGARA BARAT": "KEPULAUAN TANIMBAR",
    "MAMUJU UTARA": "PASANGKAYU",
    "MEMBERAMO RAYA": "MAMBERAMO RAYA",
}

PROVINCE_ALIASES = {
    "BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "KEP BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
    "D I YOGYAKARTA": "DI YOGYAKARTA",
}


def text_clean(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def compact_name(value: Any, is_province: bool = False, apply_alias: bool = True) -> str:
    """Normalize names for matching only; original source text is retained."""
    text = text_clean(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]+", " ", text).strip()

    if not is_province:
        prefixes = (
            "KOTA ADMINISTRASI ",
            "KABUPATEN ADMINISTRASI ",
            "KABUPATEN ",
            "KOTA ADM ",
            "KOTA ADMIN ",
            "KAB ",
            "KOTA ",
        )
        changed = True
        while changed:
            changed = False
            for prefix in prefixes:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
                    changed = True
                    break

    # Compact spelling handles API names such as "S I A K" and "D U M A I".
    text = re.sub(r"\s+", "", text)

    if not apply_alias:
        return text

    if is_province:
        alias_map = {
            re.sub(r"\s+", "", k): re.sub(r"\s+", "", v)
            for k, v in PROVINCE_ALIASES.items()
        }
    else:
        alias_map = {
            re.sub(r"\s+", "", k): re.sub(r"\s+", "", v)
            for k, v in DISTRICT_ALIASES.items()
        }

    return alias_map.get(text, text)


def display_province(value: Any) -> str:
    raw = text_clean(value).upper()
    special = {
        "DKI JAKARTA": "DKI Jakarta",
        "DI YOGYAKARTA": "DI Yogyakarta",
        "DAERAH ISTIMEWA YOGYAKARTA": "DI Yogyakarta",
        "KEPULAUAN BANGKA BELITUNG": "Kepulauan Bangka Belitung",
    }
    return special.get(raw, text_clean(value).title())


def display_region(value: Any) -> str:
    return text_clean(value).title()


def source_region_type(value: Any) -> str | None:
    raw = text_clean(value).upper()
    if raw.startswith("KOTA"):
        return "Kota"
    if raw.startswith("KABUPATEN") or raw.startswith("KAB "):
        return "Kabupaten"
    return None


def bps_region_type(code: str) -> str:
    # Struktur kode BPS kabupaten/kota: kode kota umumnya memakai kelompok 71 ke atas.
    try:
        tail = int(code[-2:])
    except (ValueError, TypeError):
        return "Tidak diketahui"
    return "Kota" if tail >= 71 else "Kabupaten"


def find_input_file() -> Path:
    candidates = [
        DATA_DIR / DEFAULT_FILENAME,
        DATA_DIR / "Dataset_Bapanas_Referensi_Wilayah_BPS(1).csv",
        PROJECT_DIR / DEFAULT_FILENAME,
        PROJECT_DIR / "Dataset_Bapanas_Referensi_Wilayah_BPS(1).csv",
    ]
    for path in candidates:
        if path.exists():
            return path

    # Fallback: search only project root and data folder, not .venv.
    patterns = [
        *DATA_DIR.glob("Dataset_Bapanas_Referensi_Wilayah_BPS*.csv"),
        *PROJECT_DIR.glob("Dataset_Bapanas_Referensi_Wilayah_BPS*.csv"),
    ]
    patterns = [p for p in patterns if p.is_file()]
    if len(patterns) == 1:
        return patterns[0]
    if len(patterns) > 1:
        raise FileNotFoundError(
            "Ditemukan lebih dari satu file dataset Bapanas. "
            "Simpan satu file sumber di folder 'data' dengan nama "
            f"'{DEFAULT_FILENAME}'."
        )
    raise FileNotFoundError(
        "File dataset tidak ditemukan. Letakkan file "
        f"'{DEFAULT_FILENAME}' di folder '{DATA_DIR}'."
    )


def fetch_json_map(session: requests.Session, year: int, detail_level: int) -> dict[str, str]:
    params = {"lv2": detail_level, "lvl": 10, "thn": year}
    url = BASE_API
    last_error = None

    for attempt in range(1, 5):
        try:
            response = session.get(url, params=params, timeout=45)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict) or not payload:
                raise ValueError(f"Respons API kosong/tidak berbentuk objek untuk tahun {year}.")

            output: dict[str, str] = {}
            for key, value in payload.items():
                code = re.sub(r"\D", "", str(key))
                name = text_clean(value)
                if code and name:
                    output[code] = name

            if not output:
                raise ValueError(f"API tidak mengembalikan kode wilayah untuk tahun {year}.")

            return output

        except Exception as exc:  # noqa: BLE001 - report the original API failure to user
            last_error = exc
            if attempt < 4:
                wait_seconds = attempt * 2
                print(
                    f"  Percobaan {attempt}/4 gagal ({exc}). "
                    f"Mencoba lagi dalam {wait_seconds} detik..."
                )
                time.sleep(wait_seconds)

    raise RuntimeError(
        f"Gagal mengambil referensi BPS tahun {year}, lv2={detail_level}. "
        f"API Sipedas sedang tidak dapat diakses. Detail: {last_error}"
    )


def build_reference(session: requests.Session, year: int) -> pd.DataFrame:
    print(f"Mengambil referensi wilayah BPS tahun {year}...")
    provinces = fetch_json_map(session, year, 11)
    districts = fetch_json_map(session, year, 12)

    rows = []
    for code, district_name in districts.items():
        code = str(code).zfill(4)
        province_code = code[:2]
        province_name = provinces.get(province_code)
        if not province_name:
            # Keep the record for audit but flag missing parent province.
            province_name = ""

        rows.append({
            "Tahun": year,
            "Kode_Wilayah_BPS": code,
            "Kode_Provinsi_BPS": province_code,
            "Provinsi_BPS_Referensi": display_province(province_name),
            "Kabupaten_Kota_BPS_Referensi": display_region(district_name),
            "Tipe_Wilayah_BPS": bps_region_type(code),
            "_prov_key": compact_name(province_name, is_province=True),
            "_kab_key": compact_name(district_name),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        raise RuntimeError(f"Referensi kabupaten/kota tahun {year} kosong.")
    if result["Kode_Wilayah_BPS"].duplicated().any():
        dup = result[result["Kode_Wilayah_BPS"].duplicated(False)]
        raise RuntimeError(
            f"Referensi BPS tahun {year} memuat kode ganda: "
            f"{dup['Kode_Wilayah_BPS'].tolist()[:10]}"
        )
    return result


def choose_candidate(source_row: pd.Series, candidates: pd.DataFrame) -> tuple[pd.Series | None, str, str]:
    """Match by district identity and province; never force unresolved rows."""
    if candidates.empty:
        return None, "TIDAK_DITEMUKAN", "Tidak ada nama wilayah yang cocok"

    src_prov = source_row["_prov_key"]
    src_type = source_region_type(source_row["Kabupaten_Kota_Bapanas_Asli"])
    src_code = source_row["Kode_Wilayah_Bapanas"]
    name_method = source_row["Metode_Normalisasi_Nama"]

    same_province = candidates[candidates["_prov_key"] == src_prov]

    if len(same_province) == 1:
        chosen = same_province.iloc[0]
        status = "COCOK_PROVINSI_DAN_NAMA"
        if name_method == "ALIAS" or source_row["_prov_alias"]:
            status = "COCOK_DENGAN_ALIAS_DAN_PROVINSI"
        return chosen, status, "Nama wilayah cocok di provinsi yang sama"

    if len(same_province) > 1:
        pool = same_province.copy()
        if src_type:
            typed = pool[pool["Tipe_Wilayah_BPS"] == src_type]
            if len(typed) == 1:
                return typed.iloc[0], "COCOK_NAMA_PROVINSI_DAN_TIPE", "Nama dan tipe wilayah cocok"
            if not typed.empty:
                pool = typed
        code_match = pool[pool["Kode_Wilayah_BPS"] == src_code]
        if len(code_match) == 1:
            return (
                code_match.iloc[0],
                "COCOK_NAMA_PROVINSI_DENGAN_KODE_SEBAGAI_PEMBEDA",
                "Nama cocok; kode sumber hanya dipakai sebagai pemecah ambiguitas",
            )
        return None, "AMBIGU_BEBERAPA_KANDIDAT", "Nama wilayah memiliki lebih dari satu kandidat dalam provinsi"

    # If source province is wrong, only auto-map when the district name is unique nationally.
    if len(candidates) == 1:
        chosen = candidates.iloc[0]
        return (
            chosen,
            "NAMA_UNIK_PROVINSI_SUMBER_BERBEDA_PERLU_TINJAUAN",
            "Nama wilayah unik secara nasional tetapi provinsi sumber berbeda",
        )

    if len(candidates) > 1:
        pool = candidates.copy()
        if src_type:
            typed = pool[pool["Tipe_Wilayah_BPS"] == src_type]
            if len(typed) == 1:
                return (
                    typed.iloc[0],
                    "NAMA_DAN_TIPE_UNIK_PROVINSI_SUMBER_BERBEDA_PERLU_TINJAUAN",
                    "Nama dan tipe cocok tetapi provinsi sumber berbeda",
                )
        return None, "AMBIGU_PROVINSI_BERBEDA", "Nama wilayah muncul di beberapa provinsi"

    return None, "TIDAK_DITEMUKAN", "Tidak ada kandidat yang sesuai"


def main() -> int:
    print("=" * 68)
    print("PEMBUATAN CROSSWALK WILAYAH BAPANAS - BPS 2021-2023")
    print("Dataset sumber tidak akan ditimpa atau diubah.")
    print("=" * 68)

    input_file = find_input_file()
    print(f"Dataset sumber: {input_file}")

    df = pd.read_csv(
        input_file,
        encoding="utf-8-sig",
        dtype={"Kode Wilayah": "string"},
    )

    required = ["Tahun", "Kode Wilayah", "Provinsi", "Kabupaten_Kota"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing}")

    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce").astype("Int64")
    df["Kode Wilayah"] = df["Kode Wilayah"].astype("string").str.replace(r"\.0$", "", regex=True).str.strip()

    actual_years = sorted(df["Tahun"].dropna().astype(int).unique().tolist())
    if actual_years != YEARS:
        raise ValueError(
            f"Periode dataset harus 2021, 2022, 2023. Ditemukan: {actual_years}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
    })

    reference_frames = []
    for year in YEARS:
        ref = build_reference(session, year)
        reference_frames.append(ref)
        print(f"  Referensi {year}: {len(ref):,} kabupaten/kota")

    reference_all = pd.concat(reference_frames, ignore_index=True)
    ref_export = reference_all.drop(columns=["_prov_key", "_kab_key"])
    ref_export.to_csv(
        OUTPUT_DIR / "Referensi_Wilayah_BPS_2021_2023.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Build unique source-location identities AFTER normalizing whitespace/case.
    # The source CSV contains a few labels that differ only by invisible trailing
    # spaces (for example, "Sambas" and "Sambas "). If drop_duplicates() is
    # applied before text normalization, those rows remain separate and later
    # violate the many-to-one merge validation. We collapse only the lookup
    # table; every original observation remains in df and is restored below.
    locations = df[required].copy()
    locations = locations.rename(columns={
        "Kode Wilayah": "Kode_Wilayah_Bapanas",
        "Provinsi": "Provinsi_Bapanas_Asli",
        "Kabupaten_Kota": "Kabupaten_Kota_Bapanas_Asli",
    })
    locations["Kode_Wilayah_Bapanas"] = (
        locations["Kode_Wilayah_Bapanas"].astype("string")
        .str.replace(r"\.0$", "", regex=True).str.strip()
    )

    # Join keys are used only internally; the original labels are retained.
    locations["_prov_join"] = locations["Provinsi_Bapanas_Asli"].map(
        lambda x: text_clean(x).casefold()
    )
    locations["_kab_join"] = locations["Kabupaten_Kota_Bapanas_Asli"].map(
        lambda x: text_clean(x).casefold()
    )

    locations = locations.drop_duplicates(
        subset=[
            "Tahun", "Kode_Wilayah_Bapanas",
            "_prov_join", "_kab_join"
        ]
    ).copy()

    locations["_prov_key"] = locations["Provinsi_Bapanas_Asli"].map(
        lambda x: compact_name(x, is_province=True)
    )
    locations["_kab_key"] = locations["Kabupaten_Kota_Bapanas_Asli"].map(
        lambda x: compact_name(x)
    )
    locations["_prov_alias"] = locations["Provinsi_Bapanas_Asli"].map(
        lambda x: compact_name(x, is_province=True, apply_alias=False)
        != compact_name(x, is_province=True, apply_alias=True)
    )
    locations["Metode_Normalisasi_Nama"] = locations[
        "Kabupaten_Kota_Bapanas_Asli"
    ].map(lambda x: "ALIAS" if compact_name(x, apply_alias=False)
        != compact_name(x, apply_alias=True) else "NORMAL")

    results = []
    for _, source in locations.iterrows():
        year = int(source["Tahun"])
        ref = reference_all[reference_all["Tahun"] == year]
        candidate = ref[ref["_kab_key"] == source["_kab_key"]]
        chosen, status, note = choose_candidate(source, candidate)

        row = {
            "Tahun": year,
            "Kode_Wilayah_Bapanas": source["Kode_Wilayah_Bapanas"],
            "Provinsi_Bapanas_Asli": text_clean(source["Provinsi_Bapanas_Asli"]),
            "Kabupaten_Kota_Bapanas_Asli": text_clean(source["Kabupaten_Kota_Bapanas_Asli"]),
            "Kode_Wilayah_BPS": chosen["Kode_Wilayah_BPS"] if chosen is not None else "",
            "Kode_Provinsi_BPS": chosen["Kode_Provinsi_BPS"] if chosen is not None else "",
            "Provinsi_BPS_Standar_Crosswalk": chosen["Provinsi_BPS_Referensi"] if chosen is not None else "",
            "Kabupaten_Kota_BPS_Standar_Crosswalk": chosen["Kabupaten_Kota_BPS_Referensi"] if chosen is not None else "",
            "Status_Crosswalk": status,
            "Catatan_Crosswalk": note,
            "Kandidat_BPS": " | ".join(
                f"{r.Kode_Wilayah_BPS} {r.Provinsi_BPS_Referensi} - {r.Kabupaten_Kota_BPS_Referensi}"
                for r in candidate.itertuples()
            ),
            "_prov_key": source["_prov_key"],
            "_kab_key": source["_kab_key"],
            "_prov_join": source["_prov_join"],
            "_kab_join": source["_kab_join"],
        }
        results.append(row)

    crosswalk = pd.DataFrame(results)

    # Flags for a Bapanas source code reused for different identities.
    source_code_dest = (
        crosswalk[crosswalk["Kode_Wilayah_BPS"].ne("")]
        .groupby(["Tahun", "Kode_Wilayah_Bapanas"])["Kode_Wilayah_BPS"]
        .nunique()
    )
    multi_source_codes = set(
        source_code_dest[source_code_dest > 1].index.tolist()
    )
    crosswalk["Flag_Kode_Bapanas_Multi_Identitas"] = crosswalk.apply(
        lambda r: (int(r["Tahun"]), r["Kode_Wilayah_Bapanas"]) in multi_source_codes,
        axis=1,
    )

    # Flags for multiple Bapanas source identities mapped to one BPS code.
    mapped = crosswalk[crosswalk["Kode_Wilayah_BPS"].ne("")].copy()
    dest_counts = (
        mapped.groupby(["Tahun", "Kode_Wilayah_BPS"])
        .size()
    )
    duplicate_dest = set(
        dest_counts[dest_counts > 1].index.tolist()
    )
    crosswalk["Flag_Beberapa_Sumber_Menuju_BPS_Sama"] = crosswalk.apply(
        lambda r: (int(r["Tahun"]), r["Kode_Wilayah_BPS"]) in duplicate_dest
        if r["Kode_Wilayah_BPS"] else False,
        axis=1,
    )

    # Merge crosswalk back to every original row; no source rows are deleted.
    # Crosswalk already has one row per normalized source-location identity.
    df_work = df.copy()
    df_work["_kode_src"] = (
        df_work["Kode Wilayah"].astype("string")
        .str.replace(r"\.0$", "", regex=True).str.strip()
    )
    df_work["_prov_join"] = df_work["Provinsi"].map(
        lambda x: text_clean(x).casefold()
    )
    df_work["_kab_join"] = df_work["Kabupaten_Kota"].map(
        lambda x: text_clean(x).casefold()
    )

    bridge_columns = [
        "Tahun", "Kode_Wilayah_Bapanas", "_prov_join", "_kab_join",
        "Kode_Wilayah_BPS", "Kode_Provinsi_BPS",
        "Provinsi_BPS_Standar_Crosswalk",
        "Kabupaten_Kota_BPS_Standar_Crosswalk",
        "Status_Crosswalk", "Catatan_Crosswalk",
        "Flag_Kode_Bapanas_Multi_Identitas",
        "Flag_Beberapa_Sumber_Menuju_BPS_Sama",
    ]
    bridge = crosswalk[bridge_columns].copy()

    # Defensive uniqueness check before many-to-one join.
    bridge_keys = [
        "Tahun", "Kode_Wilayah_Bapanas", "_prov_join", "_kab_join"
    ]
    duplicate_bridge = bridge[bridge.duplicated(bridge_keys, keep=False)]
    if not duplicate_bridge.empty:
        raise RuntimeError(
            "Tabel crosswalk masih memiliki identitas sumber ganda setelah "
            "normalisasi. Contoh: "
            + duplicate_bridge[bridge_keys].head(10).to_string(index=False)
        )

    df_out = df_work.merge(
        bridge,
        left_on=["Tahun", "_kode_src", "_prov_join", "_kab_join"],
        right_on=["Tahun", "Kode_Wilayah_Bapanas", "_prov_join", "_kab_join"],
        how="left",
        validate="many_to_one",
    )

    if len(df_out) != len(df):
        raise RuntimeError(
            "Jumlah baris berubah setelah penggabungan crosswalk. "
            "Proses dihentikan agar tidak ada baris yang terduplikasi atau hilang."
        )

    df_out = df_out.drop(
        columns=["_kode_src", "_prov_join", "_kab_join"],
        errors="ignore",
    )

    # Export full mapping and audit reports.
    crosswalk_export = crosswalk.drop(
        columns=["_prov_key", "_kab_key", "_prov_join", "_kab_join"]
    )
    crosswalk_export.to_csv(
        OUTPUT_DIR / "Crosswalk_Bapanas_BPS_2021_2023.csv",
        index=False,
        encoding="utf-8-sig",
    )

    df_out.to_csv(
        OUTPUT_DIR / "Dataset_Bapanas_Hasil_Crosswalk_Tahap_Validasi.csv",
        index=False,
        encoding="utf-8-sig",
    )

    unresolved_or_review = crosswalk[
        ~crosswalk["Status_Crosswalk"].str.startswith("COCOK")
        | crosswalk["Flag_Kode_Bapanas_Multi_Identitas"]
        | crosswalk["Flag_Beberapa_Sumber_Menuju_BPS_Sama"]
    ].drop(columns=["_prov_key", "_kab_key", "_prov_join", "_kab_join"])
    unresolved_or_review.to_csv(
        OUTPUT_DIR / "Lokasi_Perlu_Tinjauan.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary_rows = []
    for year in YEARS:
        part = crosswalk[crosswalk["Tahun"] == year]
        summary_rows.append({
            "Tahun": year,
            "Lokasi_Sumber_Unik": len(part),
            "Berhasil_Dipetakan_Nama_Provinsi": int(part["Status_Crosswalk"].eq("COCOK_PROVINSI_DAN_NAMA").sum()),
            "Berhasil_Dipetakan_Alias_Atau_Tipe": int(part["Status_Crosswalk"].str.startswith("COCOK_").sum() - part["Status_Crosswalk"].eq("COCOK_PROVINSI_DAN_NAMA").sum()),
            "Nama_Unik_Provinsi_Berbeda": int(part["Status_Crosswalk"].str.contains("PROVINSI_SUMBER_BERBEDA", na=False).sum()),
            "Ambigu": int(part["Status_Crosswalk"].str.startswith("AMBIGU").sum()),
            "Tidak_Ditemukan": int(part["Status_Crosswalk"].eq("TIDAK_DITEMUKAN").sum()),
            "Kode_Bapanas_Multi_Identitas": int(part["Flag_Kode_Bapanas_Multi_Identitas"].sum()),
            "Beberapa_Sumber_Menuju_BPS_Sama": int(part["Flag_Beberapa_Sumber_Menuju_BPS_Sama"].sum()),
        })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(
        OUTPUT_DIR / "Ringkasan_Hasil_Crosswalk.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Bundle all outputs so the user only needs to upload one file for review.
    output_zip = OUTPUT_DIR / "Hasil_Crosswalk_Bapanas_BPS_2021_2023.zip"
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for output_file in sorted(OUTPUT_DIR.glob("*.csv")):
            archive.write(output_file, arcname=output_file.name)

    print("\n" + "=" * 68)
    print("SELESAI")
    print(f"Jumlah baris sumber       : {len(df):,}".replace(",", "."))
    print(f"Jumlah baris hasil        : {len(df_out):,}".replace(",", "."))
    print(f"Lokasi sumber unik        : {len(crosswalk):,}".replace(",", "."))
    print(f"Lokasi perlu tinjauan     : {len(unresolved_or_review):,}".replace(",", "."))
    print(f"Folder hasil              : {OUTPUT_DIR}")
    print("\nFile utama yang dihasilkan:")
    print("1. Crosswalk_Bapanas_BPS_2021_2023.csv")
    print("2. Dataset_Bapanas_Hasil_Crosswalk_Tahap_Validasi.csv")
    print("3. Lokasi_Perlu_Tinjauan.csv")
    print("4. Ringkasan_Hasil_Crosswalk.csv")
    print("5. Hasil_Crosswalk_Bapanas_BPS_2021_2023.zip (paket untuk diunggah)")
    print("\nDataset asli tidak ditimpa. Nilai konsumsi tidak diubah.")
    print("Periksa status crosswalk sebelum menyebut dataset sebagai final.")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print("\nPROSES DIHENTIKAN:")
        print(exc)
        print(
            "\nPastikan koneksi internet aktif, file CSV berada di folder data, "
            "dan library pandas serta requests sudah terpasang."
        )
        sys.exit(1)
