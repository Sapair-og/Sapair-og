"""Generate the animated "sakura night" artwork used in the profile README.

Usage: python art.py <output_dir>
Writes hero.svg, divider.svg and footer.svg. Pure SVG + SMIL/CSS animation,
so it animates inside GitHub's <img> sandbox (no JS, no external fonts).
"""
import os
import random
import sys

W = 1200
PINK, PINK_LIGHT, LAVENDER, ICE = "#F472B6", "#FBCFE8", "#A78BFA", "#7DD3FC"
SANS = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace"
JP = "'Yu Gothic', 'Hiragino Sans', 'Noto Sans JP', 'Meiryo', sans-serif"

PETAL = "M0,0 C3,-7 11,-8 13,-2 L10,0 L13,2 C11,8 3,7 0,0 Z"


def sky_defs(height):
    return f"""
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#070620"/>
    <stop offset="0.45" stop-color="#1E1B4B"/>
    <stop offset="0.8" stop-color="#4C1D6B"/>
    <stop offset="1" stop-color="#8A2D6B"/>
  </linearGradient>
  <radialGradient id="moonGlow">
    <stop offset="0" stop-color="#FFE4F1" stop-opacity="0.55"/>
    <stop offset="1" stop-color="#FFE4F1" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="textGrad" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{PINK_LIGHT}"/>
    <stop offset="0.35" stop-color="{PINK}"/>
    <stop offset="0.7" stop-color="{LAVENDER}"/>
    <stop offset="1" stop-color="{ICE}"/>
    <animate attributeName="x1" values="0;1;0" dur="8s" repeatCount="indefinite"/>
    <animate attributeName="x2" values="1;2;1" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{height}" rx="18"/></clipPath>"""


def stars(rng, count, max_y):
    out = []
    for _ in range(count):
        x, y = rng.uniform(0, W), rng.uniform(0, max_y)
        r = rng.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        dur = rng.uniform(2, 6)
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff">'
            f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur:.1f}s" '
            f'begin="-{rng.uniform(0, dur):.1f}s" repeatCount="indefinite"/></circle>'
        )
    return "\n  ".join(out)


def petals(rng, count, height):
    out = []
    for _ in range(count):
        x0 = rng.uniform(-100, W)
        dx = rng.uniform(40, 220)
        dur = rng.uniform(9, 18)
        spin = rng.uniform(3, 7) * rng.choice([1, -1])
        scale = rng.uniform(0.6, 1.3)
        color = rng.choice([PINK, PINK_LIGHT, "#F9A8D4", "#F9A8D4"])
        out.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="{x0:.0f},-20; {x0 + dx:.0f},{height + 20}" dur="{dur:.1f}s" '
            f'begin="-{rng.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="rotate" '
            f'values="0;{360 if spin > 0 else -360}" dur="{abs(spin):.1f}s" repeatCount="indefinite"/>'
            f'<path d="{PETAL}" fill="{color}" opacity="0.85" transform="scale({scale:.2f})"/></g></g>'
        )
    return "\n  ".join(out)


def moon(cx, cy, r):
    return f"""<circle cx="{cx}" cy="{cy}" r="{r * 3}" fill="url(#moonGlow)"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFF1F7"/>
  <circle cx="{cx - r * 0.35}" cy="{cy - r * 0.2}" r="{r * 0.18}" fill="#F5D0E3" opacity="0.6"/>
  <circle cx="{cx + r * 0.3}" cy="{cy + r * 0.3}" r="{r * 0.12}" fill="#F5D0E3" opacity="0.6"/>"""


def shooting_star():
    return """<g opacity="0">
    <line x1="0" y1="0" x2="-110" y2="-36" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/>
    <circle r="2.2" fill="#fff"/>
    <animateTransform attributeName="transform" type="translate" values="250,10; 820,200; 820,200" keyTimes="0;0.12;1" dur="9s" begin="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0;0" keyTimes="0;0.12;1" dur="9s" begin="2s" repeatCount="indefinite"/>
  </g>"""


def fuji(base):
    peak = base - 150
    mountain = (
        f"M560,{base} L800,{peak + 20} Q820,{peak + 5} 840,{peak + 10} L860,{peak + 3} "
        f"Q880,{peak - 3} 900,{peak + 5} L920,{peak + 10} Q940,{peak + 5} 960,{peak + 20} L1200,{base} Z"
    )
    snow = (
        f"M800,{peak + 20} Q820,{peak + 5} 840,{peak + 10} L860,{peak + 3} Q880,{peak - 3} 900,{peak + 5} "
        f"L920,{peak + 10} Q940,{peak + 5} 960,{peak + 20} L935,{peak + 37} L915,{peak + 27} L895,{peak + 45} "
        f"L875,{peak + 29} L855,{peak + 43} L835,{peak + 27} L815,{peak + 37} Z"
    )
    hills = (
        f'<path d="M0,{base} C150,{base - 60} 300,{base - 30} 420,{base - 55} C520,{base - 75} 620,{base - 20} 700,{base} Z" fill="#241A52" opacity="0.9"/>'
        f'<path d="M980,{base} C1050,{base - 50} 1120,{base - 45} 1200,{base - 70} L1200,{base} Z" fill="#241A52" opacity="0.9"/>'
    )
    return f"""<linearGradient id="mtn" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4B3A8C"/><stop offset="1" stop-color="#1A1340"/>
  </linearGradient>
  <g id="land">
    <path d="{mountain}" fill="url(#mtn)"/>
    <path d="{snow}" fill="#F3E8FF" opacity="0.92"/>
    {hills}
  </g>"""


def lake(top, height):
    lines = []
    for i, (x, w) in enumerate([(820, 120), (760, 80), (900, 70), (180, 90), (400, 60), (1050, 90)]):
        y = top + 8 + (i % 3) * 9
        lines.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="1.5" rx="1" fill="#FBCFE8" opacity="0.35">'
            f'<animate attributeName="opacity" values="0.1;0.5;0.1" dur="{3 + i % 3}s" repeatCount="indefinite"/></rect>'
        )
    return f"""<rect x="0" y="{top}" width="{W}" height="{height - top}" fill="#0B0A26" opacity="0.85"/>
  <g transform="translate(0,{2 * top}) scale(1,-1)" opacity="0.22"><use href="#land"/></g>
  {''.join(lines)}"""


def hero():
    h, base = 380, 330
    rng = random.Random(7)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs>{sky_defs(h)}
  <linearGradient id="tail" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  {fuji(base)}
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{h}" fill="url(#sky)"/>
  {stars(rng, 70, 260)}
  {moon(1085, 78, 36)}
  {shooting_star()}
  <use href="#land"/>
  {lake(base, h)}
  <g>
    <text x="62" y="108" font-family="{JP}" font-size="18" letter-spacing="6" fill="{PINK}">ヤシュヴァルダン ・ こんにちは！</text>
  </g>
  <g filter="url(#glow)">
    <text x="60" y="162" font-family="{SANS}" font-size="46" font-weight="800" fill="url(#textGrad)">Yashvardhan Singh Sarangdevot</text>
  </g>
  <g>
    <text x="62" y="202" font-family="{SANS}" font-size="21" font-weight="600" fill="#E0E7FF">Python • GenAI Applications Developer</text>
  </g>
  <rect x="62" y="220" width="330" height="3" rx="1.5" fill="url(#textGrad)"/>
  <g>
    <text x="62" y="256" font-family="{MONO}" font-size="16" fill="{ICE}">&gt; agentic AI · RAG · computer vision <tspan>▋<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></tspan></text>
  </g>
  {petals(rng, 26, h)}
</g>
</svg>
"""


def divider():
    h = 36
    flower = "".join(
        f'<path d="{PETAL}" fill="{PINK}" transform="translate(600,18) rotate({a}) translate(3,0) scale(0.75)"/>'
        for a in range(0, 360, 72)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs>
  <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{ICE}" stop-opacity="0"/>
    <stop offset="0.3" stop-color="{LAVENDER}"/>
    <stop offset="0.5" stop-color="{PINK}"/>
    <stop offset="0.7" stop-color="{LAVENDER}"/>
    <stop offset="1" stop-color="{ICE}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="spark"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="60" y="17" width="500" height="2" rx="1" fill="url(#ln)"/>
<rect x="640" y="17" width="500" height="2" rx="1" fill="url(#ln)"/>
<circle cy="18" r="7" fill="url(#spark)">
  <animate attributeName="cx" values="60;560;560;640;1140" keyTimes="0;0.45;0.5;0.55;1" dur="5s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;0;1;0" keyTimes="0;0.4;0.5;0.6;1" dur="5s" repeatCount="indefinite"/>
</circle>
<g>{flower}<circle cx="600" cy="18" r="2.5" fill="{PINK_LIGHT}"/>
  <animateTransform attributeName="transform" type="rotate" values="0 600 18;360 600 18" dur="12s" repeatCount="indefinite"/>
</g>
</svg>
"""


def footer():
    h = 190
    rng = random.Random(11)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs>{sky_defs(h)}</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{h}" fill="url(#sky)"/>
  {stars(rng, 45, 130)}
  {moon(600, 52, 24)}
  <rect x="0" y="135" width="{W}" height="55" fill="#0B0A26" opacity="0.85"/>
  <ellipse cx="600" cy="150" rx="40" ry="3" fill="#FFE4F1" opacity="0.45">
    <animate attributeName="rx" values="30;55;30" dur="4s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="600" cy="162" rx="22" ry="2" fill="#FFE4F1" opacity="0.3">
    <animate attributeName="rx" values="18;36;18" dur="5s" repeatCount="indefinite"/>
  </ellipse>
  <text x="600" y="108" text-anchor="middle" font-family="{SANS}" font-size="24" font-weight="700" fill="url(#textGrad)" filter="url(#glow)">Thanks for visiting!</text>
  <text x="600" y="180" text-anchor="middle" font-family="{JP}" font-size="14" letter-spacing="4" fill="{PINK}">またね ・ see you soon</text>
  {petals(rng, 14, h)}
</g>
</svg>
"""


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "assets"
    os.makedirs(out, exist_ok=True)
    for name, svg in (("hero.svg", hero()), ("divider.svg", divider()), ("footer.svg", footer())):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(svg)


if __name__ == "__main__":
    main()
