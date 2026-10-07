"""Evan van Dongen design system, as static HTML building blocks.

Mirrors the design system's React components (Post, BarChart, Stamp) with the
same class names, so the vendored `assets/bundle.css` styles them exactly as
the design system does. Tokens come from the vendored `assets/tokens.json`.
To pick up design-system changes, re-copy tokens.json and bundle.css.
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
CANVAS = {"portrait": (1080, 1350), "square": (1080, 1080), "landscape": (1200, 627)}


def esc(text) -> str:
    return html.escape(str(text), quote=True)


# ------------------------------------------------------------------ tokens ---

def _resolve(value, theme, by_name, seen=()):
    if isinstance(value, dict):
        value = value.get(theme, value.get("light"))
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        ref = value[1:-1]
        if ref in seen:
            raise ValueError(f"token alias loop at {ref}")
        return _resolve(by_name[ref]["value"], theme, by_name, seen + (ref,))
    return value


def token_vars(theme: str) -> dict[str, str]:
    """All design tokens as CSS custom properties for one theme ('light' = Paper, 'dark' = Ink)."""
    tokens = json.loads((ASSETS / "tokens.json").read_text())
    colors = {t["name"]: t for t in tokens["color"]["tokens"]}
    out = {f"--{n}": _resolve(t["value"], theme, colors) for n, t in colors.items()}
    for family in ("spacing", "radius", "size", "stroke", "shadow"):
        for t in tokens.get(family, {}).get("tokens", []):
            v = t["value"]
            out[f"--{t['name']}"] = v.get(theme, v.get("light")) if isinstance(v, dict) else v
    for role, stack in tokens["type"]["families"].items():
        out[f"--font-{role}"] = stack
    return out


def css_block(selector: str, props: dict[str, str]) -> str:
    body = "".join(f"  {k}: {v};\n" for k, v in props.items())
    return f"{selector} {{\n{body}}}\n"


def fonts_css(prefix: str = "") -> str:
    """@font-face rules; `prefix` is the path from the HTML file to assets/."""
    return (ASSETS / "fonts.css").read_text().replace("url('fonts/", f"url('{prefix}fonts/")


def bundle_css() -> str:
    return (ASSETS / "bundle.css").read_text()


def icon(name: str, size: int = 144) -> str:
    """Inline one of the design system's square icon tiles."""
    svg = (ASSETS / "icons" / f"{name}.svg").read_text()
    return svg.replace('width="96" height="96"', f'width="{size}" height="{size}"', 1)


# ------------------------------------------------------------- components ---

def post(*, title="", kicker="", standfirst="", body="", source="", page="",
         tone="paper", title_size="l", align="start", byline="Evan van Dongen",
         size="portrait", corner_icon="") -> str:
    w, h = CANVAS[size]
    classes = ["evd-post", f"evd-post--{tone}", f"evd-post--{size}"]
    if title_size == "xl":
        classes.append("evd-post--xl")
    head = ""
    if kicker or title or standfirst:
        head = (
            '<header class="evd-post__head">'
            + (f'<p class="evd-post__kicker">{esc(kicker)}</p>' if kicker else "")
            + (f'<h1 class="evd-post__title">{esc(title)}</h1>' if title else "")
            + (f'<p class="evd-post__standfirst">{esc(standfirst)}</p>' if standfirst else "")
            + "</header>"
        )
    corner = f'<div class="slide-icon">{corner_icon}</div>' if corner_icon else ""
    body_cls = "evd-post__body" + (" evd-post__body--center" if align == "center" else "")
    sign = (f'<span class="evd-post__byline">{esc(byline)}</span>' if byline else "") + (
        f'<span class="evd-post__page">{esc(page)}</span>' if page else "")
    return (
        f'<article class="{" ".join(classes)}" style="width:{w}px;height:{h}px">'
        '<span class="evd-post__tab" aria-hidden="true"></span>'
        f"{corner}{head}"
        f'<div class="{body_cls}">{body}</div>'
        f'<footer class="evd-post__foot"><span class="evd-post__source">{esc(source)}</span>'
        f'<span class="evd-post__sign">{sign}</span></footer>'
        "</article>"
    )


def stamp(value, *, label="", unit="", caption="", tone="red", size="m", fraction="") -> str:
    frac = ""
    if fraction:
        num, den = fraction.split("/")
        frac = (f'<span class="evd-stamp__frac"><span class="evd-stamp__num">{esc(num)}</span>'
                f'<span class="evd-stamp__den">{esc(den)}</span></span>')
    return (
        f'<figure class="evd-stamp-wrap evd-stamp-wrap--{size}">'
        f'<div class="evd-stamp evd-stamp--{tone}"><div class="evd-stamp__field">'
        + (f'<span class="evd-stamp__label">{esc(label)}</span>' if label else "")
        + f'<span class="evd-stamp__value">{esc(value)}{frac}</span>'
        + (f'<span class="evd-stamp__unit">{esc(unit)}</span>' if unit else "")
        + "</div></div>"
        + (f'<figcaption class="evd-stamp__caption">{esc(caption)}</figcaption>' if caption else "")
        + "</figure>"
    )


def _nice_step(span: float, count: int) -> float:
    raw = span / count
    mag = 10 ** math.floor(math.log10(raw))
    n = raw / mag
    step = 1 if n <= 1 else 2 if n <= 2 else 2.5 if n <= 2.5 else 5 if n <= 5 else 10
    return step * mag


def ticks(lo: float, hi: float, count: int = 4) -> list[float]:
    if lo == hi:
        hi = lo + 1
    st = _nice_step(hi - lo, count)
    start = math.floor(lo / st + 1e-9) * st
    end = math.ceil(hi / st - 1e-9) * st
    out, v = [], start
    while v <= end + st / 2:
        out.append(round(v, 6))
        v += st
    return out


def fmt_num(v: float, unit: str = "", decimals: int | None = None) -> str:
    s = f"{abs(v):.{decimals}f}" if decimals is not None else f"{round(abs(v), 2):g}"
    if unit:
        s = unit + s if unit in "€$£" else s + unit
    return ("−" if v < 0 else "") + s


def bar_chart(data: list[tuple[str, float]], *, subtitle="", highlight=(), unit="", tick_unit="",
              width=936, label_width=300, bar_height=52, gap=24, max_value=None,
              decimals=None, tick_count=4) -> str:
    """Horizontal Economist-style bar chart (the BarChart component with rule: false)."""
    highlight = set(highlight)
    vals = [v for _, v in data]
    tk = ticks(min([0, *vals]), max_value if max_value is not None else max([0, *vals]), tick_count)
    lo, hi = tk[0], tk[-1]
    top, plot_x = 56, label_width
    plot_w = width - label_width - 128
    x = lambda v: plot_x + (v - lo) / (hi - lo) * plot_w  # noqa: E731
    height = top + len(data) * (bar_height + gap) - gap + 8
    parts = []
    for t in tk:
        cls = "evd-axis" if t == 0 else "evd-grid"
        parts.append(f'<line class="{cls}" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top - 12}" y2="{height}"/>')
        parts.append(f'<text class="evd-tick" x="{x(t):.1f}" y="{top - 28}" text-anchor="middle">'
                     f"{esc(fmt_num(t, tick_unit))}</text>")
    for i, (label, v) in enumerate(data):
        y = top + i * (bar_height + gap)
        hi_on = label in highlight
        x0, w = x(min(0, v)), abs(x(v) - x(0))
        parts.append(f'<rect class="evd-bar{" evd-bar--hi" if hi_on else ""}" x="{x0:.1f}" y="{y}" '
                     f'width="{max(w, 1):.1f}" height="{bar_height}"/>')
        parts.append(f'<text class="evd-cat{" evd-cat--hi" if hi_on else ""}" x="{label_width - 20}" '
                     f'y="{y + bar_height / 2}" dominant-baseline="central" text-anchor="end">{esc(label)}</text>')
        parts.append(f'<text class="evd-val{" evd-val--hi" if hi_on else ""}" x="{x(v) + 12:.1f}" '
                     f'y="{y + bar_height / 2}" dominant-baseline="central">{esc(fmt_num(v, unit, decimals))}</text>')
    sub = f'<p class="evd-chart__subtitle">{esc(subtitle)}</p>' if subtitle else ""
    return (f'<figure class="evd-chart" style="width:{width}px">{sub}'
            f'<svg class="evd-chart__plot" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{esc(subtitle or "Bar chart")}">{"".join(parts)}</svg></figure>')


def table(headers: list[str], rows: list[list[str]], *, highlight_rows=(), numeric_from: int = 1) -> str:
    """A carousel table: paper-sunk header, hairline rows, green-tint for the row the slide is about."""
    th = "".join(f'<th class="{"num" if i >= numeric_from else ""}">{esc(h)}</th>' for i, h in enumerate(headers))
    body = []
    for r, row in enumerate(rows):
        cls = ' class="is-hi"' if r in highlight_rows else ""
        tds = "".join(f'<td class="{"num" if i >= numeric_from else ""}">{esc(c)}</td>' for i, c in enumerate(row))
        body.append(f"<tr{cls}>{tds}</tr>")
    return f'<table class="slide-table"><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def rows_list(items: list[tuple[str, str]], *, detail_class="slide-list__detail") -> str:
    """Label on the left in the serif, a short value on the right in the narrow face."""
    lis = "".join(f'<li><span class="slide-list__name">{esc(a)}</span>'
                  f'<span class="{detail_class}">{esc(b)}</span></li>' for a, b in items)
    return f'<ul class="slide-list">{lis}</ul>'


# Extra rules for things the design system has no component for (tables, lists,
# corner icons, print pagination). Built only from its tokens.
SLIDE_EXTRAS_CSS = """
@page { size: 1080px 1350px; margin: 0; }
html, body { margin: 0; padding: 0; background: var(--paper); }
.deck { display: block; }
.deck > .evd-post { break-after: page; page-break-after: always; }
.deck > .evd-post:last-child { break-after: auto; page-break-after: auto; }
.slide-icon { position: absolute; top: var(--space-9); right: var(--space-9); line-height: 0; }
.slide-icon svg { display: block; }
.evd-post:has(.slide-icon) .evd-post__head { padding-right: 176px; }
.slide-body { font: 400 34px/48px var(--font-serif); font-optical-sizing: auto; margin: 0; max-width: 30em; }
.slide-body + .slide-body { margin-top: var(--space-3); }
.slide-table { width: 100%; border-collapse: collapse; font: 500 30px/36px var(--font-narrow); color: var(--ink); }
.slide-table th { background: var(--paper-sunk); font: 700 24px/30px var(--font-narrow); letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--ink-muted); text-align: left; padding: 14px 12px; }
.slide-table td { padding: 20px 12px; border-bottom: var(--stroke-grid) solid var(--rule); }
.slide-table .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.slide-table td.num:last-child { font-weight: 700; }
.slide-table tr.is-hi td { background: var(--green-tint); font-weight: 700; }
.slide-list { list-style: none; margin: 0; padding: 0; border-top: var(--stroke-axis) solid var(--ink); }
.slide-list li { display: flex; justify-content: space-between; align-items: baseline; gap: var(--space-4);
  padding: 14px 0; border-bottom: var(--stroke-grid) solid var(--rule); }
.slide-list__name { font: 400 34px/44px var(--font-serif); }
.slide-list__detail { font: 700 30px/36px var(--font-narrow); color: var(--green); white-space: nowrap; font-variant-numeric: tabular-nums; }
.slide-list--plain .slide-list__name { font-size: 36px; line-height: 48px; }
.slide-split { display: flex; gap: var(--space-6); align-items: center; }
.slide-split > :first-child { flex: 1 1 auto; min-width: 0; }
.slide-note { font: 400 24px/30px var(--font-narrow); color: var(--ink-muted); margin: var(--space-3) 0 0; }
.slide-bottom { margin-top: auto; }
.evd-post--green .slide-body { color: var(--on-green); }
"""


def deck_html(slides: list[str], *, title: str, asset_prefix: str) -> str:
    """A full HTML document holding 1080x1350 slides, one per PDF page."""
    root = css_block(":root", token_vars("light"))
    return (
        "<!doctype html><html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
        f"<title>{esc(title)}</title>"
        f"<style>{fonts_css(asset_prefix)}\n{root}\n{bundle_css()}\n{SLIDE_EXTRAS_CSS}</style>"
        f"</head><body><main class=\"deck\">{''.join(slides)}</main></body></html>"
    )
