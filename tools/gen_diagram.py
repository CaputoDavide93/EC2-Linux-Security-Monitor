#!/usr/bin/env python3
"""Draw this repository's diagrams as SVG, one file per colour scheme.

  docs/assets/<name>-light.svg
  docs/assets/<name>-dark.svg

Drawn rather than written in Mermaid, because GitHub renders Mermaid on its
own terms: it picks the theme, pins the version, ignores styling, and decodes
HTML entities before parsing. Drawn here, there is one rule instead: **GitHub
sanitises SVG in markdown**, so no <style>, no <script>, no web font and no
<foreignObject>. Every colour is a presentation attribute and the type is a
system stack. Each pair is served from one <picture>, which GitHub switches on
prefers-color-scheme.

Layout is explicit rather than solved. The diagrams are small enough that
placing them by hand is cheaper than a layout engine nobody can predict.

House rules: a slate scale, a single accent on the one component that matters
in each picture, drawn icons rather than emoji, monospace for anything that is
literally typed, and text contrast at or above 4.5:1 in both schemes.

Standard library only. After changing a diagram, run:

  python3 tools/gen_diagram.py
"""
from __future__ import annotations

import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
SANS = "system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

SCHEMES = {
    "light": dict(card="#ffffff", border="#d8dee4", title="#0f172a", sub="#5b6673",
                  accent="#2b59c3", on_accent="#ffffff", soft="#f1f4f9",
                  line="#94a3b8", rule="#e6e9ee", chip="#475569",
                  warn="#9a3412", warn_soft="#fff4ed", group="#f7f9fb"),
    "dark":  dict(card="#161b22", border="#30363d", title="#e6edf3", sub="#9aa4b0",
                  accent="#4c7ef3", on_accent="#ffffff", soft="#1b2230",
                  line="#6b7684", rule="#232a33", chip="#aeb7c2",
                  warn="#ffa657", warn_soft="#2a1d14", group="#11151b"),
}

# Stroked glyphs on a 24x24 grid, drawn rather than typed.
ICONS = {
    "clock":    "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7v5l3 2",
    "shield":   "M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z M8.5 12l2.5 2.5 4.5-4.5",
    "wrench":   "M14.7 6.3a4 4 0 0 1 5-1.5l-2.6 2.6.5 2 2 .5 2.6-2.6a4 4 0 0 1-5.4 5.1L10 19.2"
                "a2 2 0 0 1-2.8-2.8l6.8-6.8a4 4 0 0 1 .7-3.3z",
    "sliders":  "M4 6h9 M17 6h3 M15 4v4 M4 12h3 M11 12h9 M9 10v4 M4 18h11 M19 18h1 M17 16v4",
    "download": "M12 3v12 M7 10l5 5 5-5 M4 20h16",
    "refresh":  "M20 11a8 8 0 0 0-14.3-4.9L4 8 M4 3v5h5 M4 13a8 8 0 0 0 14.3 4.9L20 16 M20 21v-5h-5",
    "bug":      "M9 7a3 3 0 0 1 6 0 M7 9h10v5a5 5 0 0 1-10 0z M12 9v10 M3 12h4 M17 12h4 "
                "M4 7l3 2.5 M20 7l-3 2.5 M4 19l3-2.5 M20 19l-3-2.5",
    "document": "M6 3h8l4 4v14H6z M14 3v4h4 M9 12h6 M9 16h6",
    "lock":     "M5 11h14v10H5z M8 11V7a4 4 0 0 1 8 0v4 M12 15v2",
    "bell":     "M6 16v-5a6 6 0 0 1 12 0v5l2 2H4z M10 21h4",
    "chart":    "M4 4v16h16 M8 16v-4 M12 16V8 M16 16v-6",
    "pulse":    "M3 12h4l2-5 4 10 2-5h6",
    "package":  "M12 3l8 4.5v9L12 21l-8-4.5v-9z M4 7.5l8 4.5 8-4.5 M12 12v9",
}


class Canvas:
    """Parts plus a size. No layout engine, on purpose."""

    def __init__(self, w: int, h: int, scheme: str, label: str) -> None:
        self.w, self.h, self.c, self.label = w, h, SCHEMES[scheme], label
        self.parts: list[str] = []

    def add(self, *svg: str) -> "Canvas":
        self.parts.extend(svg)
        return self

    # ── primitives ────────────────────────────────────────────────────────
    def icon(self, name, x, y, colour, size=21):
        s = size / 24
        return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" fill="none" '
                f'stroke="{colour}" stroke-width="1.7" stroke-linecap="round" '
                f'stroke-linejoin="round"><path d="{ICONS[name]}"/></g>')

    def text(self, x, y, s, *, size=13, colour=None, font=None, weight=None,
             anchor="start", opacity=None):
        c = colour or self.c["sub"]
        extra = (f' font-weight="{weight}"' if weight else "") + \
                (f' opacity="{opacity}"' if opacity else "")
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font or SANS}" '
                f'font-size="{size}" fill="{c}" text-anchor="{anchor}"{extra}>'
                f'{escape(s)}</text>')

    def box(self, x, y, w, h, title, subs=(), *, icon=None, tone="plain", rx=10):
        c = self.c
        fill, edge, tt = c["card"], c["border"], c["title"]
        st, op = c["sub"], ""
        if tone == "accent":
            fill = edge = c["accent"]; tt = st = c["on_accent"]; op = "0.85"
        elif tone == "soft":
            fill = c["soft"]
        elif tone == "warn":
            fill, edge, tt, st = c["warn_soft"], c["warn"], c["warn"], c["warn"]
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
               f'stroke="{edge}" stroke-width="1"/>']
        tx = x + 16
        ty = y + (28 if subs else h / 2 + 5)
        if icon:
            out.append(self.icon(icon, x + 16, y + (13 if subs else h / 2 - 10), tt))
            tx = x + 47
        out.append(self.text(tx, ty, title, size=15 if subs else 14,
                             colour=tt, weight="600"))
        for i, s in enumerate(subs):
            out.append(self.text(x + 16, y + 52 + i * 18, s, size=12.5,
                                 colour=st, opacity=op or None))
        return "".join(out)

    def diamond(self, cx, cy, w, h, lines):
        c = self.c
        pts = f"{cx},{cy - h/2} {cx + w/2},{cy} {cx},{cy + h/2} {cx - w/2},{cy}"
        out = [f'<polygon points="{pts}" fill="{c["soft"]}" stroke="{c["border"]}" '
               f'stroke-width="1"/>']
        n = len(lines)
        for i, s in enumerate(lines):
            out.append(self.text(cx, cy - (n - 1) * 7 + i * 14 + 4, s, size=12,
                                 colour=c["title"], anchor="middle"))
        return "".join(out)

    def pill(self, cx, cy, text, *, tone="plain", pad=16, size=13):
        c = self.c
        w = len(text) * size * 0.58 + pad * 2
        h = 32
        fill, edge, col = c["card"], c["border"], c["title"]
        if tone == "accent":
            fill = edge = c["accent"]; col = c["on_accent"]
        elif tone == "soft":
            fill = c["soft"]
        return (f'<rect x="{cx - w/2:.1f}" y="{cy - h/2}" width="{w:.1f}" height="{h}" '
                f'rx="{h/2}" fill="{fill}" stroke="{edge}" stroke-width="1"/>'
                + self.text(cx, cy + 4.5, text, size=size, colour=col, anchor="middle",
                            weight="500")), w

    def edge(self, pts, *, label=None, dash=False, both=False, label_at=0.5,
             label_dy=-9, label_anchor="middle", mono=True):
        c = self.c
        d = ' stroke-dasharray="5 4"' if dash else ""
        path = " ".join(f"{x},{y}" for x, y in pts)
        out = [f'<polyline points="{path}" fill="none" stroke="{c["line"]}" '
               f'stroke-width="1.5"{d} marker-end="url(#a)"'
               + (' marker-start="url(#a)"' if both else "") + "/>"]
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            lx = x1 + (x2 - x1) * label_at
            ly = y1 + (y2 - y1) * label_at
            out.append(self.text(lx, ly + label_dy, label, size=11.5,
                                 colour=c["chip"], font=MONO if mono else SANS,
                                 anchor=label_anchor))
        return "".join(out)

    def group(self, x, y, w, h, title):
        c = self.c
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
                f'fill="{c["group"]}" stroke="{c["border"]}" stroke-width="1" '
                f'stroke-dasharray="6 5"/>'
                + self.text(x + 18, y + 24, title, size=12, colour=c["sub"],
                            weight="600"))

    def footer(self, note):
        return (f'<line x1="24" y1="{self.h - 52}" x2="{self.w - 24}" y2="{self.h - 52}" '
                f'stroke="{self.c["rule"]}" stroke-width="1"/>'
                + self.text(24, self.h - 26, note, size=12.5, colour=self.c["sub"]))

    def render(self) -> str:
        c = self.c
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-label="{escape(self.label)}">'
            f'<defs>'
            f'<marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 10 5 0 10z" fill="{c["line"]}"/></marker>'
            f'</defs>' + "".join(self.parts) + "</svg>"
        )


def card(k, x, y, w, h, title, subs=(), *, mono=(), icon=None, tone="plain"):
    """A Canvas box whose sub-lines at the indices in `mono` are set in monospace.

    Canvas.box sets every sub-line in the sans stack. Paths, commands and flags
    are literally typed, so they are swapped for the monospace stack here,
    in place, with the box's own position and colour.
    """
    svg = k.box(x, y, w, h, title, subs, icon=icon, tone=tone)
    colour = {"accent": k.c["on_accent"], "warn": k.c["warn"]}.get(tone, k.c["sub"])
    opacity = "0.85" if tone == "accent" else None
    for i in mono:
        at = dict(size=12.5, colour=colour, opacity=opacity)
        sans = k.text(x + 16, y + 52 + i * 18, subs[i], **at)
        assert sans in svg, f"sub-line {i} of {title!r} not found"
        svg = svg.replace(sans, k.text(x + 16, y + 52 + i * 18, subs[i], font=MONO,
                                       **dict(at, size=12)), 1)
    return svg


def note(k, x, y, s, *, mono=True, anchor="start"):
    """An edge label placed by hand, for vertical and diagonal edges."""
    return k.text(x, y, s, size=11.5, font=MONO if mono else SANS,
                  colour=k.c["chip"], anchor=anchor)


# ── the diagrams ──────────────────────────────────────────────────────────

def architecture(scheme):
    """Two scripts, two timers, one config file, and what each run touches."""
    k = Canvas(1180, 700, scheme,
               "The scan timer runs security-monitor, which refreshes definitions, applies updates, "
               "scans with clamscan and writes status.json; infected files are quarantined and "
               "alerted on, and the status dashboard reads the result. The health timer runs "
               "security-manager, which repairs services, definitions and timers. Both scripts "
               "source one config file.")
    c = k.c
    x1, W1 = 44, 188
    x2, W2 = 288, 220
    x3, W3 = 556, 240
    x4, W4 = 876, 280
    H, h = 92, 64
    steps = [102, 202, 302, 402]
    row, health = 88, 514
    sx = x3 + W3 / 2
    k.add(
        k.group(24, 40, 228, 586, "SYSTEMD TIMERS"),
        card(k, x1, row, W1, H, "Scan timer", ["SCAN_SCHEDULE", "02:00 daily"], mono=[0], icon="clock"),
        card(k, x1, health, W1, H, "Health timer", ["HEALTH_SCHEDULE", "every 6 hours"], mono=[0], icon="clock"),
        k.text(24 + 114, 336, "Persistent=true", size=11.5, font=MONO, colour=c["chip"], anchor="middle"),
        k.text(24 + 114, 356, "a run missed while the", size=12, anchor="middle"),
        k.text(24 + 114, 373, "instance was stopped", size=12, anchor="middle"),
        k.text(24 + 114, 390, "happens on next boot", size=12, anchor="middle"),
        card(k, x2, row, W2, H, "security-monitor", ["scan [quick|full]", "as root"], mono=[0],
             icon="shield", tone="accent"),
        card(k, x2, 315, W2, h, "Config file", ["security-monitor.conf"], mono=[0], icon="sliders"),
        card(k, x2, health, W2, H, "security-manager", ["health", "as root"], mono=[0], icon="wrench"),
        # The scan, in the order the script runs it.
        card(k, x3, steps[0], W3, h, "Refresh definitions", ["freshclam"], mono=[0], icon="download"),
        card(k, x3, steps[1], W3, h, "Apply updates", ["apt-get / dnf upgrade"], mono=[0], icon="refresh"),
        card(k, x3, steps[2], W3, h, "Scan for malware", ["clamscan -r -i"], mono=[0], icon="bug"),
        card(k, x3, steps[3], W3, h, "Write the result", ["status.json"], mono=[0], icon="document"),
        card(k, x4, steps[1], W4, h, "Quarantine", ["QUARANTINE_DIR, mode 0700"], mono=[0], icon="lock"),
        card(k, x4, steps[2], W4, h, "Alert", ["ALERT_COMMAND"], mono=[0], icon="bell"),
        card(k, x4, steps[3], W4, h, "Status dashboard", ["security-monitor status"], mono=[0], icon="chart"),
        card(k, x3, health, x4 + W4 - x3, H, "Health checks",
             ["restarts dead services and re-downloads stale definitions,",
              "re-enables stopped timers, checks the installed scripts and config"], icon="pulse"),
        k.edge([(x1 + W1 + 8, row + H / 2), (x2 - 8, row + H / 2)]),
        k.edge([(x1 + W1 + 8, health + H / 2), (x2 - 8, health + H / 2)]),
        k.edge([(x2 + W2 + 8, row + H / 2), (x3 - 8, row + H / 2)]),
        k.edge([(x2 + W2 + 8, health + H / 2), (x3 - 8, health + H / 2)]),
        k.edge([(sx, steps[0] + h + 8), (sx, steps[1] - 8)]),
        k.edge([(sx, steps[1] + h + 8), (sx, steps[2] - 8)]),
        k.edge([(sx, steps[2] + h + 8), (sx, steps[3] - 8)]),
        k.edge([(x3 + W3 + 8, steps[2] + 16), (x4 - 8, steps[1] + h - 20)]),
        note(k, 850, 292, "--move"),
        k.edge([(x3 + W3 + 8, steps[2] + h / 2 + 6), (x4 - 8, steps[2] + h / 2 + 6)],
               label="infected", mono=False),
        k.edge([(x3 + W3 + 8, steps[3] + h / 2), (x4 - 8, steps[3] + h / 2)], label="read by", mono=False),
        # One file, sourced by both scripts.
        k.edge([(x2 + W2 / 2, 315 - 8), (x2 + W2 / 2, row + H + 8)], dash=True),
        k.edge([(x2 + W2 / 2, 315 + h + 8), (x2 + W2 / 2, health - 8)], dash=True),
        note(k, x2 + W2 / 2 + 10, (row + H + 315) / 2 + 4, "sourced by", mono=False),
        note(k, x2 + W2 / 2 + 10, (315 + h + health) / 2 + 4, "sourced by", mono=False),
        k.footer("A schedule or a path is stated once, in the config file. The health check repairs "
                 "what the scan depends on, so a stopped timer or a stale database does not go unnoticed."),
    )
    return k.render()


def scan_sequence(scheme):
    """One scheduled scan, end to end, in the order security-monitor runs it."""
    k = Canvas(1180, 580, scheme,
               "The scan timer starts security-monitor, which runs freshclam with the service "
               "paused, upgrades packages, runs clamscan and reads its exit code, writes "
               "status.json, sends the findings to ALERT_COMMAND only if files were infected, "
               "and prunes old scan logs.")
    c = k.c
    T, M, C, P, A = 124, 354, 594, 830, 1052
    lanes = [("Scan timer", T, "clock"), ("security-monitor", M, "shield"),
             ("ClamAV", C, "bug"), ("apt / dnf", P, "package"), ("ALERT_COMMAND", A, "bell")]
    top, bottom = 84, 512
    for name, x, icon in lanes:
        w = 196
        tone = "accent" if x == M else "plain"
        k.add(k.box(x - w / 2, 26, w, 44, name, icon=icon, tone=tone),
              f'<line x1="{x}" y1="{top - 14}" x2="{x}" y2="{bottom}" stroke="{c["border"]}" '
              f'stroke-width="1" stroke-dasharray="4 5"/>')

    def msg(y, x1, x2, text, *, dash=False, mono=True, at=0.5):
        d = 8 if x2 > x1 else -8
        return k.edge([(x1 + d, y), (x2 - d, y)], label=text, dash=dash, mono=mono, label_at=at)

    def self_msg(y, x, text):
        return (k.edge([(x, y), (x + 54, y), (x + 54, y + 26), (x + 6, y + 26)]) +
                k.text(x + 66, y + 4, text, size=11.5, font=MONO, colour=c["chip"]))

    # The alt block: the one decision in a scan.
    k.add(f'<rect x="{T + 40}" y="366" width="{A + 96 - T - 40}" height="76" rx="8" fill="none" '
          f'stroke="{c["border"]}" stroke-width="1" stroke-dasharray="5 4"/>',
          k.text(T + 54, 384, "if infected files were found", size=11.5, colour=c["sub"], weight="600"))
    k.add(
        msg(104, T, M, "scan $SCAN_MODE"),
        msg(144, M, C, "freshclam, service paused"),
        # Labels to the package manager sit between its lifeline and ClamAV's.
        msg(184, M, P, "upgrade what is pending", at=0.761),
        msg(218, P, M, "applied, still available", dash=True, mono=False, at=0.239),
        msg(258, M, C, "clamscan -r -i --move"),
        msg(292, C, M, "exit 0 clean, 1 infected, 2+ error", dash=True, mono=False),
        self_msg(322, M, "write status.json"),
        msg(420, M, A, "subject and findings on stdin", mono=False),
        self_msg(466, M, "prune old scan logs"),
        k.footer("A dashed arrow is a reply. The result is written before the alert is sent, "
                 "so the dashboard is current even when the alert command fails."),
    )
    return k.render()


DIAGRAMS = {
    "architecture": architecture,
    "scan-sequence": scan_sequence,
}


def main() -> None:
    out = ROOT / "docs" / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in DIAGRAMS.items():
        for scheme in SCHEMES:
            path = out / f"{name}-{scheme}.svg"
            path.write_text(fn(scheme), encoding="utf-8")
    print(f"{len(DIAGRAMS)} diagrams x {len(SCHEMES)} schemes -> docs/assets/")


if __name__ == "__main__":
    main()
