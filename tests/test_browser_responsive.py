"""
Pengujian Desain dan Responsivitas Browser (READ-ONLY)
Menguji UI-01, UI-02, dan UI-03 via Playwright (Chrome Headless) pada 3 viewport:
- Desktop: 1366 x 768 px
- Tablet: 768 x 1024 px
- Smartphone: 390 x 844 px
"""

from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8501"
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "blackbox_readonly_final"
SHOT_DIR = REPORT_DIR / "screenshots"
SHOT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("desktop_1366x768", 1366, 768),
    ("tablet_768x1024", 768, 1024),
    ("mobile_390x844", 390, 844),
]


def check_overlaps(boxes: list[dict]) -> list[str]:
    issues = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ox = min(a["right"], b["right"]) - max(a["left"], b["left"])
            oy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
            if ox > 2 and oy > 2:
                issues.append(f"KPI {i} overlaps KPI {j} ({ox:.1f}x{oy:.1f}px)")
    return issues


def run_browser_audit():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for name, w, h in VIEWPORTS:
            context = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
            page = context.new_page()
            console_errors = []
            page_errors = []
            external_failed = []
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on(
                "requestfailed",
                lambda req: external_failed.append(req.url) if not req.url.startswith(BASE_URL) else None,
            )

            page.goto(BASE_URL, wait_until="networkidle", timeout=45000)
            page.wait_for_selector(".kpi-card", timeout=30000)
            page.wait_for_selector('[data-testid="stPlotlyChart"]', timeout=30000)
            page.wait_for_timeout(1500)

            page.screenshot(path=str(SHOT_DIR / f"{name}_dashboard.png"), full_page=False)

            metrics = page.evaluate(
                """() => {
                const vw = window.innerWidth;
                const docScrollW = document.documentElement.scrollWidth;
                const appEl = document.querySelector('.stApp');
                const appStyle = appEl ? getComputedStyle(appEl) : null;
                const heroEl = document.querySelector('.header-hero');
                const heroStyle = heroEl ? getComputedStyle(heroEl) : null;
                const heroRect = heroEl ? heroEl.getBoundingClientRect() : null;
                const sidebar = document.querySelector('section[data-testid="stSidebar"]');
                const sidebarExpanded = sidebar ? sidebar.getAttribute('aria-expanded') : null;

                const kpis = Array.from(document.querySelectorAll('.kpi-card')).map(el => {
                    const r = el.getBoundingClientRect();
                    return {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height};
                });
                const charts = Array.from(document.querySelectorAll('[data-testid="stPlotlyChart"]')).map((el, idx) => {
                    const r = el.getBoundingClientRect();
                    return {idx, width: r.width, height: r.height, right: r.right, overflowsRight: r.right > vw + 2};
                });
                return {
                    viewportWidth: vw,
                    docScrollWidth: docScrollW,
                    hasHorizontalOverflow: docScrollW > vw + 2,
                    appBgColor: appStyle ? appStyle.backgroundColor : null,
                    appHasBgImage: appStyle ? appStyle.backgroundImage !== 'none' : false,
                    appTextColor: appStyle ? appStyle.color : null,
                    heroHasBgImage: heroStyle ? heroStyle.backgroundImage !== 'none' : false,
                    heroVisible: !!heroRect && heroRect.width > 0 && heroRect.height > 0,
                    sidebarExpanded,
                    kpiCount: kpis.length,
                    kpis,
                    chartCount: charts.length,
                    chartOverflows: charts.filter(c => c.overflowsRight).map(c => c.idx),
                };
            }"""
            )
            kpi_overlaps = check_overlaps(metrics["kpis"])
            kpi_overflows = [i for i, k in enumerate(metrics["kpis"]) if k["right"] > w + 2]

            # Buka sidebar jika tertutup untuk navigasi ke Tabel Data Konsumsi
            if metrics["sidebarExpanded"] == "false":
                toggle = page.locator('[data-testid="stSidebarCollapsedControl"] button, button[kind="headerNoPadding"]').first
                if toggle.count() > 0:
                    toggle.click()
                    page.wait_for_timeout(600)

            page.locator("label").filter(has_text="Tabel Data Konsumsi").first.click()
            page.wait_for_selector('[data-testid="stDataFrame"]', timeout=25000)
            page.wait_for_timeout(1200)
            page.screenshot(path=str(SHOT_DIR / f"{name}_tabel.png"), full_page=False)

            table_info = page.evaluate(
                """() => {
                const vw = window.innerWidth;
                const df = document.querySelector('[data-testid="stDataFrame"]');
                const dfRect = df ? df.getBoundingClientRect() : null;
                const dlBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Unduh'));
                const dlRect = dlBtn ? dlBtn.getBoundingClientRect() : null;
                return {
                    dfVisible: !!dfRect && dfRect.width > 0,
                    dfWidth: dfRect ? dfRect.width : 0,
                    dfRightExceedsViewport: dfRect ? dfRect.right > vw + 2 : false,
                    dlBtnVisible: !!dlRect && dlRect.width > 0,
                    docScrollWidthOnTable: document.documentElement.scrollWidth,
                };
            }"""
            )

            results[name] = {
                "viewport": f"{w}x{h}",
                "console_errors": console_errors,
                "page_errors": page_errors,
                "external_failed": external_failed,
                "metrics": metrics,
                "kpi_overlaps": kpi_overlaps,
                "kpi_overflows": kpi_overflows,
                "table_info": table_info,
            }
            context.close()
        browser.close()

    with open(REPORT_DIR / "browser_audit_raw.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps({
        k: {
            "viewport": v["viewport"],
            "hasHorizontalOverflow": v["metrics"]["hasHorizontalOverflow"],
            "appBgColor": v["metrics"]["appBgColor"],
            "appHasBgImage": v["metrics"]["appHasBgImage"],
            "heroHasBgImage": v["metrics"]["heroHasBgImage"],
            "sidebarExpanded": v["metrics"]["sidebarExpanded"],
            "kpiCount": v["metrics"]["kpiCount"],
            "kpi_overlaps": v["kpi_overlaps"],
            "chartCount": v["metrics"]["chartCount"],
            "chartOverflows": v["metrics"]["chartOverflows"],
            "table_info": v["table_info"],
            "errors": len(v["console_errors"]) + len(v["page_errors"]),
        }
        for k, v in results.items()
    }, indent=2))


if __name__ == "__main__":
    run_browser_audit()

