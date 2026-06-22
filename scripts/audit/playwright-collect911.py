#!/usr/bin/env python3
"""Collect theme 9-11 data for all samples via Playwright page.evaluate (same JS as MCP CDP)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT = ROOT / "audits" / "cmvmediforce" / "2026-06-22"
SCRIPTS = ROOT / "scripts" / "audit"
EXPR = (SCRIPTS / "theme911-only-collect.js").read_text(encoding="utf-8")
SAVE = SCRIPTS / "save-cdp-value911.py"
SAMPLES = json.loads((AUDIT / "samples-status.json").read_text(encoding="utf-8"))["samples"]

SIMULATION_STEPS = """
async (page) => {
  await page.goto('https://www.cmvmediforce.fr/simulation', {waitUntil: 'networkidle'});
  await page.evaluate(() => document.getElementById('accept-recommended-btn-handler')?.click());
  await page.waitForTimeout(500);
  await page.click('#vehicle');
  await page.waitForTimeout(300);
  const therm = page.locator('input[name="vehicle-type[]"], input[id*="therm"], label:has-text("Thermique")').first();
  if (await therm.count()) await therm.click();
  await page.fill('#professions-autocomplete, input[name="professions-autocomplete"]', 'Médecin généraliste');
  await page.waitForTimeout(500);
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await page.fill('#amount, input[name="amount"]', '30000');
  await page.click('input[name="simulation-start"], button[type="submit"]');
  await page.waitForURL('**/resultat-de-la-simulation**', {timeout: 30000});
}
"""


def collect_resultat_simulation(page):
    page.goto("https://www.cmvmediforce.fr/simulation", wait_until="networkidle", timeout=60000)
    page.evaluate("() => document.getElementById('accept-recommended-btn-handler')?.click()")
    time.sleep(0.5)
    page.locator('input[value="vehicles"], #vehicle, label:has-text("Véhicule")').first.click()
    time.sleep(0.5)
    for sel in [
        'label:has-text("Thermique")',
        'label:has-text("Hybride")',
        'input[name="vehicle-type[]"]',
    ]:
        loc = page.locator(sel).first
        if loc.count():
            loc.click()
            break
    time.sleep(0.3)
    prof = page.locator('#professions-autocomplete, input[name="professions-autocomplete"]').first
    prof.click()
    prof.fill("Médecin généraliste")
    time.sleep(1)
    page.locator('.ui-autocomplete li, [role="option"], .autocomplete-suggestion').filter(has_text="Médecin généraliste").first.click(timeout=5000)
    page.locator('#amount, input[name="amount"]').first.fill("30000")
    page.locator('input[name="simulation-start"], button:has-text("Simuler"), input[value="Simuler"]').first.click()
    page.wait_for_url("**/resultat-de-la-simulation**", timeout=90000)
    return page.url


def collect_sample(page, sample: dict) -> dict:
    slug, url = sample["slug"], sample["url"]
    if slug == "resultat-simulation":
        url = collect_resultat_simulation(page)
    else:
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.evaluate("() => document.getElementById('accept-recommended-btn-handler')?.click()")
        time.sleep(0.3)
    return page.evaluate(EXPR)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for s in SAMPLES:
            if s.get("status") != "ok":
                continue
            if target != "all" and s["slug"] != target:
                continue
            print(f"collecting {s['slug']}...", flush=True)
            try:
                val = collect_sample(page, s)
                tmp = Path(f"/tmp/collect911-{s['slug']}.json")
                tmp.write_text(json.dumps(val, ensure_ascii=False), encoding="utf-8")
                subprocess.run(
                    [sys.executable, str(SAVE), str(AUDIT), s["slug"], val.get("url", s["url"]), str(tmp)],
                    check=True,
                )
            except Exception as e:
                print(f"ERROR {s['slug']}: {e}", file=sys.stderr)
        browser.close()
    print("batch collect911 complete")


if __name__ == "__main__":
    main()
