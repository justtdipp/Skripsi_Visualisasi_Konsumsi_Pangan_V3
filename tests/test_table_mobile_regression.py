"""
Regression Check Terisolasi: Kontainer Tabel Data Konsumsi pada Mobile, Tablet, dan Desktop
"""

from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8501"
SHOT_DIR = Path(__file__).resolve().parent.parent / "reports" / "blackbox_readonly_final" / "screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("mobile_390x844", 390, 844),
    ("tablet_768x1024", 768, 1024),
    ("desktop_1366x768", 1366, 768),
]


def run_regression():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for name, w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))

            page.goto(BASE_URL, wait_until="networkidle", timeout=45000)
            page.wait_for_selector("label", timeout=25000)

            # Buka halaman Tabel Data Konsumsi
            page.locator("label").filter(has_text="Tabel Data Konsumsi").first.click()
            page.wait_for_selector('[data-testid="stDataFrame"]', timeout=25000)
            page.wait_for_timeout(1200)

            # Tutup sidebar pada layar kecil (mobile/tablet) agar tabel terlihat penuh seperti penggunaan nyata
            if w <= 1024:
                close_btn = page.locator('section[data-testid="stSidebar"] button').first
                if close_btn.count() > 0 and close_btn.is_visible():
                    close_btn.click()
                    page.wait_for_timeout(600)

            df_el = page.locator('[data-testid="stDataFrame"]').first
            df_el.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            page.screenshot(path=str(SHOT_DIR / f"retest_{name}_tabel.png"), full_page=False)

            info = page.evaluate(
                """() => {
                const vw = window.innerWidth;
                const docScrollW = document.documentElement.scrollWidth;
                const df = document.querySelector('[data-testid="stDataFrame"]');
                const dfRect = df ? df.getBoundingClientRect() : null;
                const dfStyle = df ? getComputedStyle(df) : null;
                const scroller = df ? (df.querySelector('.dvn-scroller') || df.querySelector('[data-testid="stDataFrameResizable"]') || df.firstElementChild) : null;
                return {
                    viewportWidth: vw,
                    docScrollWidth: docScrollW,
                    pageHorizontalOverflow: docScrollW > vw + 1,
                    dfLeft: dfRect ? Math.round(dfRect.left) : null,
                    dfRight: dfRect ? Math.round(dfRect.right) : null,
                    dfWidth: dfRect ? Math.round(dfRect.width) : null,
                    dfFrameFitsViewport: dfRect ? (dfRect.left >= -1 && dfRect.right <= vw + 1) : false,
                    dfOverflowXStyle: dfStyle ? dfStyle.overflowX : null,
                    internalScrollWidth: scroller ? scroller.scrollWidth : null,
                    internalClientWidth: scroller ? scroller.clientWidth : null,
                    hasInternalHorizontalScroll: scroller ? scroller.scrollWidth > scroller.clientWidth : false,
                };
            }"""
            )
            info["pageErrors"] = errs
            results[name] = info
            context.close()
        browser.close()

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run_regression()
