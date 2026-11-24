from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    page = context.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))

    page.goto("http://localhost:8501", wait_until="networkidle", timeout=45000)
    page.locator("label").filter(has_text="Tabel Data Konsumsi").first.click()
    page.wait_for_selector('[data-testid="stDataFrame"]', timeout=25000)
    page.wait_for_timeout(1500)

    df_el = page.locator('[data-testid="stDataFrame"]').first
    df_el.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT_DIR / "desktop_1366x768_tabel_verified.png"))

    # Trigger CSV download directly from browser UI
    dl_btn = page.locator("button").filter(has_text="Unduh Seluruh Data Sesuai Filter").first
    dl_btn.scroll_into_view_if_needed()
    with page.expect_download(timeout=30000) as dl_info:
        dl_btn.click()
    download = dl_info.value
    dl_path = OUT_DIR.parent / "temp_browser_download.csv"
    download.save_as(str(dl_path))

    df_csv = pd.read_csv(dl_path, low_memory=False)
    print("Downloaded filename:", download.suggested_filename)
    print("CSV shape:", df_csv.shape)
    print("CSV columns (15):", list(df_csv.columns))
    assert len(df_csv.columns) == 15, f"Expected 15 columns, got {len(df_csv.columns)}"
    assert "Flag Anomali Sumber" in df_csv.columns
    assert "Catatan Pembersihan Nilai" in df_csv.columns
    assert len(df_csv) == 52428
    print("Page errors:", errs)
    dl_path.unlink(missing_ok=True)
    browser.close()
