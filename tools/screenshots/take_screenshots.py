#!/usr/bin/env python3
"""Take the README screenshots of the status dashboard, from the real script.

    make screenshots     # builds .venv-screenshots on first use, needs Docker

1. Runs `security-monitor.sh status` (the repo's script, unmodified) in a
   throwaway ubuntu:24.04 container, with the demo fixtures that
   demo-dashboard.sh creates: a clean scan six hours ago, signatures one day
   old, and stand-ins for systemctl and sigtool.
2. Renders the ANSI output as a terminal window in Chromium (Playwright), in a
   light and a dark theme.
3. Saves docs/assets/screenshots/dashboard-{light,dark}.png, re-saved without
   any metadata.

Demo data only: no real host, address or file names appear.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "screenshots"
IMAGE = "ubuntu:24.04"

THEMES = {
    "light": {
        "page": "#EEF1F5", "window": "#FFFFFF", "bar": "#E3E7ED", "fg": "#1F2933",
        "title": "#52606D", "border": "#CBD2D9",
        "c": {"31": "#B42318", "32": "#15803D", "33": "#A16207", "34": "#1D4ED8",
              "36": "#0E7490", "37": "#111827", "90": "#6B7280"},
    },
    "dark": {
        "page": "#0D1117", "window": "#161B22", "bar": "#21262D", "fg": "#C9D1D9",
        "title": "#8B949E", "border": "#30363D",
        "c": {"31": "#F85149", "32": "#3FB950", "33": "#D29922", "34": "#58A6FF",
              "36": "#39C5CF", "37": "#F0F6FC", "90": "#8B949E"},
    },
}

SGR = re.compile(r"\x1b\[([0-9;]*)m")


def ansi_to_html(text: str, colours: dict[str, str]) -> str:
    out: list[str] = []
    open_span = False
    pos = 0
    for m in SGR.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        pos = m.end()
        if open_span:
            out.append("</span>")
            open_span = False
        codes = [c for c in m.group(1).split(";") if c]
        colour = next((colours[c] for c in codes if c in colours), None)
        bold = "1" in codes
        if colour or bold:
            style = (f"color:{colour};" if colour else "") + ("font-weight:700;" if bold else "")
            out.append(f'<span style="{style}">')
            open_span = True
    out.append(html.escape(text[pos:]))
    if open_span:
        out.append("</span>")
    return "".join(out)


def run_dashboard() -> str:
    proc = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{ROOT}:/src:ro", IMAGE, "bash", "-c",
         "apt-get update -qq >/dev/null && apt-get install -y -qq jq >/dev/null "
         "&& /src/tools/screenshots/demo-dashboard.sh"],
        capture_output=True, text=True, check=True,
    )
    # The script clears the screen first; drop that and keep the card output.
    text = re.sub(r"\x1b\[[0-9;?]*[HJ]|\x1b\[3J|\x1bc", "", proc.stdout)
    return text.strip("\n")


def page(body: str, t: dict) -> str:
    return f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;padding:32px;background:{t['page']};width:690px}}
.win{{background:{t['window']};border:1px solid {t['border']};border-radius:12px;overflow:hidden}}
.bar{{background:{t['bar']};padding:10px 14px;color:{t['title']};
  font:13px -apple-system,Helvetica,Arial,sans-serif}}
pre{{margin:0;padding:16px 18px;color:{t['fg']};font:13px/1.35 Menlo,"DejaVu Sans Mono",monospace;
  white-space:pre}}
</style><div class="win"><div class="bar">security-monitor status</div><pre>{body}</pre></div>"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    text = run_dashboard()
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch()
        for name, theme in THEMES.items():
            ctx = browser.new_context(viewport={"width": 754, "height": 600}, device_scale_factor=2)
            pg = ctx.new_page()
            pg.set_content(page(ansi_to_html(text, theme["c"]), theme))
            raw = Path(tmp) / f"{name}.png"
            pg.screenshot(path=raw, full_page=True)
            ctx.close()
            img = Image.open(raw).convert("RGB")
            clean = Image.frombytes("RGB", img.size, img.tobytes())  # no metadata
            clean.save(OUT / f"dashboard-{name}.png", optimize=True)
            print(f"wrote dashboard-{name}.png")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
