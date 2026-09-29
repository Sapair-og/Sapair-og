"""Render a self-hosted GitHub stats card (SVG) for the profile README.

Usage: GITHUB_TOKEN=... python stats.py <username> <output.svg>
Runs daily in the snake workflow so the card never depends on a public stats instance.
"""
import json
import os
import sys
import urllib.request
from html import escape

PALETTE = ["#F472B6", "#A78BFA", "#7DD3FC", "#FBCFE8", "#C084FC", "#38BDF8"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def top_languages(repos, limit=6):
    totals = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    langs = [(n, s / grand * 100, PALETTE[i]) for i, (n, s) in enumerate(ranked[:limit])]
    rest = sum(s for _, s in ranked[limit:]) / grand * 100
    if rest >= 0.5:
        langs.append(("Other", rest, "#64748B"))
    return langs


def render(user):
    repos = user["repositories"]["nodes"]
    cc = user["contributionsCollection"]
    stats = [
        ("Contributions (last year)", cc["contributionCalendar"]["totalContributions"]),
        ("Commits (last year)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("Public repositories", user["repositories"]["totalCount"]),
        ("Languages used", len({e["node"]["name"] for r in repos for e in r["languages"]["edges"]})),
    ]
    langs = top_languages(repos)

    width, height = 820, 250
    rows = []
    for i, (label, value) in enumerate(stats):
        y = 88 + i * 38
        rows.append(
            f'<g class="fade" style="animation-delay:{0.1 + i * 0.08:.2f}s">'
            f'<circle cx="34" cy="{y - 5}" r="4" class="dot"/>'
            f'<text x="48" y="{y}" class="label">{escape(label)}</text>'
            f'<text x="370" y="{y}" class="value" text-anchor="end">{value:,}</text></g>'
        )

    bar_x, bar_w, bar_y = 430, 360, 72
    segs, x = [], bar_x
    for name, pct, color in langs:
        w = bar_w * pct / 100
        segs.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w:.2f}" height="10" fill="{color}"/>')
        x += w
    legend = []
    for i, (name, pct, color) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = bar_x + col * 185, 116 + row * 28
        legend.append(
            f'<g class="fade" style="animation-delay:{0.4 + i * 0.08:.2f}s">'
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>'
            f'<text x="{lx + 16}" y="{ly}" class="label">{escape(name)}</text>'
            f'<text x="{lx + 175}" y="{ly}" class="muted" text-anchor="end">{pct:.1f}%</text></g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  :root {{ --border:#4C1D95; --fg:#E0E7FF; --muted:#A5B4FC; --accent:#F472B6; }}
  text {{ font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
  .card {{ fill: url(#bg); stroke: var(--border); }}
  .title {{ font-size: 17px; font-weight: 700; fill: url(#titleGrad); }}
  .label {{ font-size: 14px; fill: var(--fg); }}
  .value {{ font-size: 14px; font-weight: 700; fill: var(--accent); }}
  .muted {{ font-size: 13px; fill: var(--muted); }}
  .dot {{ fill: var(--accent); }}
  .divider {{ stroke: var(--border); }}
  .fade {{ opacity: 0; animation: fade .6s ease-out forwards; }}
  .grow {{ transform-origin: {bar_x}px 0; animation: grow 1s ease-out forwards; transform: scaleX(0); }}
  @keyframes fade {{ to {{ opacity: 1; }} }}
  @keyframes grow {{ to {{ transform: scaleX(1); }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0F0C29"/><stop offset="1" stop-color="#2A1B4E"/></linearGradient>
  <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FBCFE8"/><stop offset="1" stop-color="#A78BFA"/></linearGradient>
</defs>
<rect class="card" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12"/>
<text x="28" y="40" class="title">GitHub Stats</text>
<text x="430" y="40" class="title">Most Used Languages</text>
<line x1="400" y1="28" x2="400" y2="{height - 28}" class="divider"/>
{''.join(rows)}
<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>
<g clip-path="url(#bar)"><g class="grow">{''.join(segs)}</g></g>
{''.join(legend)}
</svg>
"""


def main():
    login, out = sys.argv[1], sys.argv[2]
    svg = render(fetch(login, os.environ["GITHUB_TOKEN"]))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
