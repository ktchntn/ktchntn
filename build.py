"""Build terminal-style SVGs for Keegan's GitHub profile README.

Each SVG embeds a subset of JetBrains Mono (only the glyphs it uses) as base64
woff2, because GitHub serves README images through a proxy that can't fetch
external fonts.
"""
import base64, io, random
from fontTools import subset
from fontTools.ttLib import TTFont

FONT_DIR = "/home/claude/font/package/files"
OUT = "/home/claude/readme/assets"

LIME = "#c6ff00"
WHITE = "#f5f5f5"
GREY = "#8a8a8a"
DIM = "#2a2a2a"
BG = "#000000"

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def font_face(weight, text):
    path = f"{FONT_DIR}/jetbrains-mono-latin-{weight}-normal.woff2"
    f = TTFont(path)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    s = subset.Subsetter(opts)
    s.populate(text=text)
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'JBM';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def dither_path(x0, y0, w, h, cell, density_fn, seed=7):
    """Ordered (Bayer) dither: a cell is filled when density > threshold."""
    rnd = random.Random(seed)
    d = []
    cols, rows = int(w // cell), int(h // cell)
    for r in range(rows):
        for c in range(cols):
            t = (BAYER[r % 4][c % 4] + 0.5) / 16
            dens = density_fn(c / max(cols - 1, 1), r / max(rows - 1, 1))
            dens += (rnd.random() - 0.5) * 0.08
            if dens > t:
                x, y = x0 + c * cell, y0 + r * cell
                d.append(f"M{x} {y}h{cell-1}v{cell-1}h-{cell-1}z")
    return "".join(d)


def corners(x, y, w, h, n=18, color=LIME):
    p = (f"M{x} {y+n}V{y}H{x+n} M{x+w-n} {y}H{x+w}V{y+n} "
         f"M{x+w} {y+h-n}V{y+h}H{x+w-n} M{x+n} {y+h}H{x}V{y+h-n}")
    return f'<path d="{p}" fill="none" stroke="{color}" stroke-width="2"/>'


# ---------------------------------------------------------------- header ---
def header():
    W, H = 1200, 320
    prompt = "keegan@keegantech:~$ whoami"
    name = "KEEGAN TECHENTIN"
    ver = "v2.0"
    tag = ["Build.", "Break.", "Harden."]
    role = "TECHNOLOGY LEAD. ETHICAL HACKER."
    status = "[ PEN-200 · MOD 27/28 ]   [ OSCP: PENDING ]"
    regular = prompt + role + status + ver + "·"
    bold = name + "".join(tag) + " "

    # dither fades in toward the right edge, heavier at the bottom
    def dens(u, v):
        return max(0.0, (u - 0.15) * 1.05) ** 1.6 * (0.75 + 0.35 * v)

    dith = dither_path(700, 24, 476, 272, 8, dens)
    lime_bits = dither_path(1000, 24, 176, 272, 8,
                            lambda u, v: max(0, u - 0.55) ** 2 * 0.9, seed=3)

    css = f"""
{font_face(400, regular)}
{font_face(800, bold)}
text{{font-family:'JBM',ui-monospace,monospace}}
.cursor{{animation:blink 1.06s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.typer{{animation:type 1.6s steps(22,end) .4s both}}
@keyframes type{{from{{transform:translateX(0)}}to{{transform:translateX(560px)}}}}
.scan{{animation:scan 6s linear infinite}}
@keyframes scan{{from{{transform:translateY(-40px)}}to{{transform:translateY(340px)}}}}
@media (prefers-reduced-motion:reduce){{
  .cursor,.typer,.scan{{animation:none}}
  .typer{{transform:translateX(560px)}}
}}"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Keegan Techentin — Build. Break. Harden. Technology Lead. Ethical Hacker.">
<style>{css}</style>
<defs>
  <linearGradient id="sl" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{LIME}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{LIME}" stop-opacity=".07"/>
    <stop offset="1" stop-color="{LIME}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="frame"><rect x="1" y="1" width="{W-2}" height="{H-2}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{DIM}" stroke-width="2"/>
{corners(12, 12, W-24, H-24)}

<text x="48" y="70" font-size="18" fill="{GREY}"><tspan fill="{LIME}">keegan@keegantech</tspan>:~$ whoami</text>

<text x="48" y="146" font-size="56" font-weight="800" fill="{WHITE}" letter-spacing="1">{name}</text>
<text x="632" y="146" font-size="18" fill="{LIME}">· {ver}</text>

<g>
  <text x="48" y="206" font-size="40" font-weight="800" fill="{WHITE}">Build. <tspan fill="{LIME}">Break.</tspan> Harden.</text>
  <rect class="typer" x="44" y="168" width="580" height="50" fill="{BG}"/>
</g>

<path d="{dith}" fill="{WHITE}" opacity=".9"/>
<path d="{lime_bits}" fill="{LIME}"/>
<text x="48" y="250" font-size="18" fill="{GREY}" letter-spacing="2">{role}</text>
<rect class="cursor" x="478" y="236" width="11" height="18" fill="{LIME}"/>

<text x="48" y="284" font-size="14" fill="{GREY}" opacity=".75">{status}</text>

<g clip-path="url(#frame)"><rect class="scan" x="0" y="0" width="{W}" height="40" fill="url(#sl)"/></g>
</svg>"""


# ------------------------------------------------------------- skill map ---
def skillmap():
    W, H = 1200, 230
    rows = [("BUILD", 19, WHITE, "TypeScript · React · Vue · GraphQL · Node · tooling · leadership"),
            ("SHARED", 3, LIME, "Bash · Python · Rust"),
            ("BREAK", 70, LIME, "AD · lateral movement · privesc · web · AV evasion · exploitation")]
    total = 92
    title = "SKILL_MAP // 92 NODES"
    regular = title + "".join(r[0] + str(r[1]) + r[3] for r in rows) + "0123456789/·"
    css = f"""
{font_face(400, regular)}
{font_face(800, "".join(r[0] for r in rows) + "0123456789")}
text{{font-family:'JBM',ui-monospace,monospace}}"""

    bar_x, bar_w, cell = 200, 720, 8
    out = []
    for i, (label, n, color, detail) in enumerate(rows):
        y = 74 + i * 52
        frac = n / total
        filled_w = bar_w * frac
        # track
        out.append(f'<rect x="{bar_x}" y="{y-14}" width="{bar_w}" height="16" fill="none" stroke="{DIM}"/>')
        # solid part + dithered tail so bars feel "printed" rather than flat
        solid = max(0, filled_w - 48)
        out.append(f'<rect x="{bar_x+2}" y="{y-12}" width="{solid}" height="12" fill="{color}"/>')
        tail = dither_path(bar_x + 2 + solid, y - 12, min(48, filled_w), 12, 4,
                           lambda u, v: 1 - u * 0.95, seed=i)
        out.append(f'<path d="{tail}" fill="{color}"/>')
        out.append(f'<text x="48" y="{y}" font-size="18" font-weight="800" fill="{color}">{label}</text>')
        out.append(f'<text x="{bar_x+bar_w+20}" y="{y}" font-size="18" fill="{WHITE}">{n:02d}/{total}</text>')
        out.append(f'<text x="{bar_x}" y="{y+18}" font-size="12" fill="{GREY}">{detail}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Skill map: Build 19, Shared 3, Break 70 of 92 nodes.">
<style>{css}</style>
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{DIM}" stroke-width="2"/>
{corners(12, 12, W-24, H-24)}
<text x="48" y="40" font-size="14" fill="{GREY}" letter-spacing="2">{title}</text>
{''.join(out)}
</svg>"""


for fname, fn in [("header.svg", header), ("skillmap.svg", skillmap)]:
    with open(f"{OUT}/{fname}", "w") as fh:
        fh.write(fn())
    print(fname, len(open(f"{OUT}/{fname}").read()) // 1024, "KB")
