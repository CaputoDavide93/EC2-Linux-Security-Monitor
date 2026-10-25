#!/usr/bin/env python3
"""Draw docs/assets/social-preview.png (1280x640) from docs/assets/brand/icon.svg.

    .venv-screenshots/bin/python tools/social_preview.py

Upload it by hand: GitHub has no API for the social preview image.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ICON = (ROOT / "docs" / "assets" / "brand" / "icon.svg").read_text()
OUT = ROOT / "docs" / "assets" / "social-preview.png"
CHIPS = ["ClamAV scans", "Quarantine", "Auto updates", "systemd timers"]

HTML = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;width:1280px;height:640px;background:#0D1117;color:#F0F6FC;
  font-family:-apple-system,Helvetica,Arial,sans-serif;display:flex;align-items:center;
  padding:0 96px;box-sizing:border-box;gap:64px}}
.icon{{width:224px;flex:none}}
h1{{font-size:68px;line-height:1.05;margin:0 0 20px;letter-spacing:-1px}}
p{{font-size:30px;line-height:1.35;margin:0 0 36px;color:#9DA7B3}}
.chips{{display:flex;gap:12px;flex-wrap:wrap}}
.chip{{font-size:22px;padding:8px 18px;border-radius:999px;background:#1F2A37;color:#C9D1D9}}
</style><div class="icon">{ICON}</div><div>
<h1>EC2 Linux Security Monitor</h1>
<p>Malware scans, quarantine and security updates for Ubuntu and Amazon Linux servers.</p>
<div class="chips">{''.join(f'<span class="chip">{c}</span>' for c in CHIPS)}</div></div>"""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 640})
        page.set_content(HTML)
        page.screenshot(path=OUT)
        browser.close()
    img = Image.open(OUT).convert("RGB")
    Image.frombytes("RGB", img.size, img.tobytes()).save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
