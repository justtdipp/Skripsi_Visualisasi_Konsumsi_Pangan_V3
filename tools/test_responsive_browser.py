"""
Responsive Browser Testing untuk Website V3
Menggunakan Playwright (Chrome headless) pada 3 ukuran viewport:
1. Desktop: 1366 x 768 px
2. Tablet: 768 x 1024 px
3. Smartphone: 390 x 844 px
"""

from __future__ import annotations

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8501"
OUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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
            # Check if two boxes overlap by more than 2px
            overlap_x = min(a["right"], b["right"]) - max(a["left"], b["left"])
            overlap_y = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
            if overlap_x > 2 and overlap_y > 2:
                issues.append(f"Card {i} overlaps Card {j} ({overlap_x:.1f}x{overlap_y:.1f}px)")
    return issues


def run_tests():
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for name, width, height in VIEWPORTS:
            print(f"\n=== Testing Viewport: {name} ({width}x{height}) ===")
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            console_errors = []
            page_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(BASE_URL, wait_until="networkidle", timeout=45000)
            # Wait for Streamlit KPI cards and Plotly charts to render
            page.wait_for_selector(".kpi-card", timeout=30000)
            page.wait_for_selector('[data-testid="stPlotlyChart"]', timeout=30000)
            page.wait_for_timeout(2000)

            # Take Dashboard screenshot
            page.screenshot(path=str(OUT_DIR / f"{name}_dashboard.png"), full_page=False)

            metrics = page.evaluate(
                """() => {
                const vw = window.innerWidth;
                const docScrollW = document.documentElement.scrollWidth;
                const appEl = document.querySelector('.stApp');
                const appStyle = appEl ? getComputedStyle(appEl) : null;
                const heroEl = document.querySelector('.header-hero');
                const heroRect = heroEl ? heroEl.getBoundingClientRect() : null;

                const sidebar = document.querySelector('section[data-testid="stSidebar"]');
                const sidebarRect = sidebar ? sidebar.getBoundingClientRect() : null;
                const sidebarExpanded = sidebar ? sidebar.getAttribute('aria-expanded') : null;

                const kpis = Array.from(document.querySelectorAll('.kpi-card')).map(el => {
                    const r = el.getBoundingClientRect();
                    return {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height};
                });

                const charts = Array.from(document.querySelectorAll('[data-testid="stPlotlyChart"]')).map((el, idx) => {
                    const r = el.getBoundingClientRect();
                    return {idx, left: r.left, right: r.right, width: r.width, height: r.height, overflowsRight: r.right > vw + 2};
                });

                const selects = Array.from(document.querySelectorAll('div[data-baseweb="select"]')).map((el, idx) => {
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
                    heroVisible: !!heroRect && heroRect.width > 0 && heroRect.height > 0,
                    heroOverflows: heroRect ? heroRect.right > vw + 2 : false,
                    sidebarExpanded,
                    sidebarWidth: sidebarRect ? sidebarRect.width : 0,
                    kpiCount: kpis.length,
                    kpis,
                    chartCount: charts.length,
                    charts,
                    selectCount: selects.length,
                    selectOverflows: selects.filter(s => s.overflowsRight).length,
                };
            }"""
            )

            kpi_overlaps = check_overlaps(metrics["kpis"])
            kpi_overflows = [i for i, k in enumerate(metrics["kpis"]) if k["right"] > width + 2]
            chart_overflows = [c["idx"] for c in metrics["charts"] if c["overflowsRight"]]

            # Test Sidebar accessibility on Tablet/Mobile
            sidebar_accessible = True
            if metrics["sidebarExpanded"] == "false":
                toggle_btn = page.locator('[data-testid="stSidebarCollapsedControl"] button, button[kind="headerNoPadding"]').first
                if toggle_btn.count() > 0:
                    toggle_btn.click()
                    page.wait_for_timeout(800)
                else:
                    sidebar_accessible = False

            # Navigate to Tabel Data Konsumsi
            radio_table = page.locator('label:has-text("Tabel Data Konsumsi")').first
            radio_table.click()
            page.wait_for_selector('[data-testid="stDataFrame"]', timeout=25000)
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT_DIR / f"{name}_tabel.png"), full_page=False)

            table_metrics = page.evaluate(
                """() => {
                const vw = window.innerWidth;
                const df = document.querySelector('[data-testid="stDataFrame"]');
                const dfRect = df ? df.getBoundingClientRect() : null;
                const dlBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Unduh'));
                const dlRect = dlBtn ? dlBtn.getBoundingClientRect() : null;
                return {
                    dfVisible: !!dfRect && dfRect.width > 0 && dfRect.height > 0,
                    dfWidth: dfRect ? dfRect.width : 0,
                    dfOverflowsPage: dfRect ? dfRect.right > vw + 2 : false,
                    dlBtnVisible: !!dlRect && dlRect.width > 0 && dlRect.height > 0,
                    dlBtnOverflows: dlRect ? dlRect.right > vw + 2 : false,
                    docScrollWidthOnTable: document.documentElement.scrollWidth,
                };
            }"""
            )

            report[name] = {
                "viewport": f"{width}x{height}",
                "console_errors": console_errors,
                "page_errors": page_errors,
                "metrics": metrics,
                "kpi_overlaps": kpi_overlaps,
                "kpi_overflows": kpi_overflows,
                "chart_overflows": chart_overflows,
                "sidebar_accessible": sidebar_accessible,
                "table_metrics": table_metrics,
            }
            print(json.dumps({
                "viewport": f"{width}x{height}",
                "hasHorizontalOverflow": metrics["hasHorizontalOverflow"],
                "docScrollWidth": metrics["docScrollWidth"],
                "appBgColor": metrics["appBgColor"],
                "appHasBgImage": metrics["appHasBgImage"],
                "heroVisible": metrics["heroVisible"],
                "kpiCount": metrics["kpiCount"],
                "kpi_overlaps": kpi_overlaps,
                "kpi_overflows": kpi_overflows,
                "chartCount": metrics["chartCount"],
                "chart_overflows": chart_overflows,
                "sidebar_accessible": sidebar_accessible,
                "table_metrics": table_metrics,
                "console_errors_count": len(console_errors),
                "page_errors_count": len(page_errors),
            }, indent=2))
            context.close()
        browser.close()

    with open(OUT_DIR.parent / "responsive_test_raw.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    run_tests()
