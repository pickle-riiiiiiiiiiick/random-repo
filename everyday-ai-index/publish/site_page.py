"""The shareable web page: method plus every edition's results, in the design system.

The output is an Artifact page body (no <html>/<head>/<body>; the host adds them).
It is regenerated from the edition data on every build, so republishing it after a
new edition keeps the same link up to date.
"""

from __future__ import annotations

import datetime as dt
import math
import tomllib
from pathlib import Path

from ds import bundle_css, css_block, esc, icon, stamp, token_vars

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/pickle-riiiiiiiiiiick/random-repo/tree/main/everyday-ai-index"
LAYER_NAMES = {"A": "Model benchmarks", "B": "App usability", "C": "My blind tests", "D": "Cost and limits"}
LAYER_HELP = {
    "A": "Independent tests of finished work: GDPval, hallucination rate, tool use, METR time horizon, "
         "blind human preference. Exam-style tests like MMLU are left out.",
    "B": "A 0–4 checklist of things I can see in the app, from file handling to asking before it deletes something.",
    "C": "Twelve errands from my own month, run in every app and graded blind with the names hidden.",
    "D": "What I'd pay per month, and how often I hit a limit.",
}
CAUSES = [
    ("Benchmarks test the model. I use a product.",
     "A leaderboard number is the model plus a test rig built by experts. I get the model plus whatever app it "
     "ships in. On Terminal-Bench 2.0 the same model moves more than 20 points depending only on the harness."),
    ("Short, clean tests hide the gap.",
     "Epoch AI puts open-weight models about four months behind. The gap is small on chat and wider on long, "
     "multi-step work, which is what a real day looks like."),
    ("Famous tests leak into training.",
     "Once a benchmark is well known, its questions turn up in training data and scores rise faster than ability. "
     "The 2026 AI Index found 2–42% invalid questions on major benchmarks."),
    ("Many headline numbers are self-reported.",
     "Launch-day scores come from the model maker's own runs. Independent re-runs often land lower."),
    ("Cheap is not the same as valued.",
     "On OpenRouter, Chinese models carry about 44% of the traffic, but closed frontier models take most of the "
     "money. People pay for what works on the jobs that matter."),
]
SOURCES = [
    ("Terminal-Bench 2.0 leaderboard (morphllm)", "https://www.morphllm.com/terminal-bench-2"),
    ("Epoch AI: open vs closed capability gap", "https://epoch.ai/data-insights/open-closed-eci-gap"),
    ("METR task-completion time horizons", "https://metr.org/time-horizons/"),
    ("GDPval, ICLR 2026", "https://proceedings.iclr.cc/paper_files/paper/2026/hash/290c2430f91912204f30bbcc990fff1d-Abstract-Conference.html"),
    ("Artificial Analysis Intelligence Index", "https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2"),
    ("LMArena", "https://lmarena.ai"),
    ("OpenRouter token vs revenue share (FourWeekMBA)", "https://fourweekmba.com/ai-openrouter-us-models-token-share-deepseek-volume-revenue-spl/"),
    ("Agent benchmarks and scaffolds (Layer3 Labs)", "https://www.layer3labs.io/guides/ai-agent-benchmarks"),
]

PAGE_CSS = """
/* Layout: one editorial column on paper, like a long carousel unrolled; wide tables scroll inside their own box. */
:root { --measure: 46rem; --gutter: clamp(16px, 4vw, 40px); }
body { background: var(--paper); color: var(--ink); font-family: var(--font-serif); font-size: 18px; line-height: 1.55; }
.page { max-width: var(--measure); margin: 0 auto; padding-inline: var(--gutter); padding-block: 0 64px; position: relative; }
.page-tab { display: block; width: 64px; height: 12px; background: var(--red); }
a { color: inherit; text-decoration-color: var(--rule); text-underline-offset: 3px; }
a:hover { text-decoration-color: var(--red); }
:focus-visible { outline: 3px solid var(--red); outline-offset: 2px; }
.kicker { font: 700 13px/1.4 var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-muted); margin: 0; }
h1, h2, h3 { font-family: var(--font-display); font-weight: 800; text-transform: uppercase; letter-spacing: 0.01em; text-wrap: balance; margin: 0; }
h1 { font-size: clamp(40px, 8vw, 72px); line-height: 0.98; margin-top: 10px; }
h2 { font-size: clamp(28px, 5vw, 40px); line-height: 1.02; margin-top: 6px; }
h3 { font-size: 18px; line-height: 1.2; letter-spacing: 0.04em; }
.standfirst { font-size: clamp(20px, 2.6vw, 24px); line-height: 1.4; margin: 16px 0 0; max-width: 34em; }
.byline { display: flex; flex-wrap: wrap; gap: 6px 16px; align-items: baseline; margin-top: 24px; padding-top: 12px; border-top: 2px solid var(--ink);
  font: 500 14px/1.4 var(--font-narrow); color: var(--ink-muted); }
.byline strong { font: 700 13px/1.4 var(--font-display); letter-spacing: 0.08em; color: var(--ink); text-transform: uppercase; }
header.top { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: end; padding-top: 28px; }
header.top .stamp-slot { padding-bottom: 8px; }
section { margin-top: 64px; }
section > .kicker + h2 { margin-top: 6px; }
p { margin: 12px 0 0; max-width: 38em; }
.lede { margin-top: 12px; }
.note { font: 400 14px/1.45 var(--font-narrow); color: var(--ink-muted); }
.callout { background: var(--green-tint); color: var(--ink); padding: 14px 18px; margin-top: 20px; font: 500 16px/1.45 var(--font-narrow); }
.figure { margin: 28px 0 0; }
.figure-title { font: 800 20px/1.25 var(--font-display); margin: 0; }
.figure-sub { font: 400 15px/1.4 var(--font-narrow); margin: 4px 0 14px; }
.figure-source { font: 400 13px/1.4 var(--font-narrow); color: var(--ink-muted); margin-top: 10px; }
.bars { display: grid; gap: 8px; border-left: 3px solid var(--ink); padding: 4px 0; }
.bar-row { display: grid; grid-template-columns: minmax(8.5rem, 13rem) minmax(0, 1fr); align-items: center; gap: 12px; }
.bar-label { font: 500 15px/1.25 var(--font-narrow); text-align: right; min-width: 0; }
.bar-row.is-hi .bar-label { font-weight: 700; }
.bar-track { display: flex; align-items: center; gap: 8px; min-width: 0; }
.bar { height: 22px; width: calc((100% - 5rem) * var(--p) / 100); background: var(--series-1); flex: none; }
.bar-row.is-hi .bar { background: var(--highlight); }
.bar-val { font: 700 15px/1 var(--font-narrow); color: var(--series-1); font-variant-numeric: tabular-nums; white-space: nowrap; }
.bar-row.is-hi .bar-val { color: var(--highlight); }
.table-wrap { overflow-x: auto; margin-top: 20px; }
table.data { width: 100%; border-collapse: collapse; font: 500 15px/1.35 var(--font-narrow); min-width: 34rem; }
table.data th { background: var(--paper-sunk); color: var(--ink-muted); font: 700 12px/1.3 var(--font-narrow); letter-spacing: 0.06em; text-transform: uppercase; text-align: left; padding: 9px 10px; }
table.data td { padding: 10px; border-bottom: 2px solid var(--rule); vertical-align: top; }
table.data .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
table.data tr.is-hi td { background: var(--green-tint); font-weight: 700; }
table.data td.total { font-weight: 700; }
.list { list-style: none; padding: 0; margin: 20px 0 0; border-top: 3px solid var(--ink); }
.list li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 16px; padding: 12px 0; border-bottom: 2px solid var(--rule); }
.list .name { font-weight: 600; }
.list .val { font: 700 15px/1.6 var(--font-narrow); color: var(--green); font-variant-numeric: tabular-nums; }
.list .desc { grid-column: 1 / -1; color: var(--ink-muted); font-size: 16px; line-height: 1.45; }
.split { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: center; margin-top: 20px; }
.ed-nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.ed-nav button { font: 700 13px/1 var(--font-display); letter-spacing: 0.08em; text-transform: uppercase; padding: 10px 14px; background: transparent;
  color: var(--ink); border: 2px solid var(--ink); border-radius: 0; cursor: pointer; }
.ed-nav button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.icon-tile { line-height: 0; }
.icon-tile svg { width: 72px; height: 72px; display: block; }
footer.end { margin-top: 72px; padding-top: 12px; border-top: 2px solid var(--ink); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 24px;
  font: 400 14px/1.4 var(--font-narrow); color: var(--ink-muted); }
footer.end strong { font: 700 13px/1.4 var(--font-display); letter-spacing: 0.08em; color: var(--ink); }
.evd-stamp-wrap--s { --sw: 132px; --sh: 158px; --sl: 13px; --sv: 62px; --r: 4px; }
.evd-stamp__caption { font-size: 13px; line-height: 1.3; }
@media (max-width: 560px) {
  header.top { grid-template-columns: minmax(0, 1fr); }
  header.top .stamp-slot { display: none; }
  .bar-row { grid-template-columns: minmax(0, 1fr); gap: 4px; }
  .bar-label { text-align: left; }
  .split { grid-template-columns: minmax(0, 1fr); justify-items: start; }
}
@media (prefers-reduced-motion: no-preference) { .bar { transition: width .4s ease-out; } }
"""

SCRIPT = """
<script>
(function () {
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-ed]'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('[data-ed-panel]'));
  function show(id) {
    panels.forEach(function (p) { p.hidden = p.getAttribute('data-ed-panel') !== id; });
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-ed') === id)); });
  }
  buttons.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-ed')); }); });
  var hash = (location.hash || '').slice(1);
  if (hash && document.querySelector('[data-ed-panel="' + hash + '"]')) show(hash);
})();
</script>
"""


def _bars(rows, *, highlight=(), unit="", max_value=None, decimals=0):
    top = max_value or max([v for _, v in rows] or [1]) or 1
    out = []
    for label, v in rows:
        pct = max(0.5, v / top * 100)
        hi = " is-hi" if label in highlight else ""
        out.append(f'<div class="bar-row{hi}"><span class="bar-label">{esc(label)}</span>'
                   f'<span class="bar-track"><span class="bar" style="--p:{pct:.1f}"></span>'
                   f'<span class="bar-val">{esc(f"{v:.{decimals}f}{unit}")}</span></span></div>')
    return f'<div class="bars">{"".join(out)}</div>'


def _short(r, by_id):
    s = by_id[r.setup_id]
    return s.get("short_label") or r.label


def _edition_id(edition) -> str:
    return f"ed-{edition['number']}"


def _edition_section(edition, profile, results, warnings, setups, ed_dir, weights_cfg) -> str:
    by_id = {s["setup_id"]: s for s in setups}
    scored = [r for r in results if r.score is not None]
    ranked = [r for r in scored if not r.provisional]
    provisional = [r for r in scored if r.provisional]
    hi_id = edition.get("highlight") or (ranked or scored)[0].setup_id
    illustrative = edition.get("illustrative", False)
    date = dt.date.fromisoformat(str(edition["date"])).strftime("%-d %B %Y")
    tag = f"Edition {edition['number']}" + (" · Example" if illustrative else "") + f" · {date}"
    source = "Source: illustrative data" if illustrative else (edition.get("source") or "Source: author's tests; public leaderboards")

    parts = [f'<p class="kicker">{esc(tag)}</p><h2>{esc(edition["headline"])}</h2>']
    if edition.get("standfirst"):
        parts.append(f'<p class="standfirst">{esc(edition["standfirst"])}</p>')
    if illustrative:
        parts.append('<div class="callout">This edition uses fictional setups to show how the index works. '
                     "Real editions start with the next major model release.</div>")
    elif edition.get("trigger"):
        parts.append(f'<p class="note">{esc(edition["trigger"])}</p>')

    hi_labels = {_short(r, by_id) for r in scored if r.setup_id == hi_id}
    note = ""
    if provisional:
        note = (f'<p class="figure-source">Not ranked yet, too little data: '
                f'{esc(", ".join(_short(r, by_id) for r in provisional))}.</p>')
    parts.append(
        f'<figure class="figure"><p class="figure-title">{esc(edition.get("ranking_title", "Who gets it done"))}</p>'
        f'<p class="figure-sub">Everyday AI Index score, 0–100, {esc(profile)} profile</p>'
        + _bars([(_short(r, by_id), r.score) for r in ranked], highlight=hi_labels, max_value=100)
        + note + f'<p class="figure-source">{esc(source)}</p></figure>')

    rows = []
    for r in scored:
        cls = ' class="is-hi"' if r.setup_id == hi_id else ""
        cells = "".join(f'<td class="num">{"–" if r.layers[k] is None else f"{r.layers[k]:.0f}"}</td>' for k in "ABCD")
        gate = "–" if r.gate_multiplier == 1 else f"×{r.gate_multiplier:.2f}"
        cov = f"{r.overall_coverage:.0%}"
        rows.append(f'<tr{cls}><td>{esc(r.label)}{" *" if r.provisional else ""}</td>{cells}'
                    f'<td class="num">{gate}</td><td class="num">{cov}</td><td class="num total">{r.score:.0f}</td></tr>')
    parts.append(
        '<figure class="figure"><p class="figure-title">Where the points come from</p>'
        '<p class="figure-sub">Each layer scored 0–100, where 100 is the best setup in this edition</p>'
        '<div class="table-wrap"><table class="data"><thead><tr><th>Setup</th><th class="num">Model</th>'
        '<th class="num">App</th><th class="num">My tests</th><th class="num">Cost</th><th class="num">Gates</th>'
        f'<th class="num">Evidence</th><th class="num">Total</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
        '<p class="figure-source">Gates multiply the total for privacy, reliability or honesty problems. '
        'Evidence is how much of the score rests on measured data; * means below 70%, so provisional.</p></figure>')

    mins = [r for r in scored if r.anchors.get("minutes_per_success") is not None
            and math.isfinite(r.anchors["minutes_per_success"])]
    if mins:
        mins.sort(key=lambda r: r.anchors["minutes_per_success"])
        parts.append(
            '<figure class="figure"><p class="figure-title">Minutes per finished task</p>'
            '<p class="figure-sub">My own time per successful task, prompting and fixing included. Lower is better</p>'
            + _bars([(_short(r, by_id), r.anchors["minutes_per_success"]) for r in mins],
                    highlight=hi_labels, unit=" min")
            + f'<p class="figure-source">{esc(source)}</p></figure>')

    by_model: dict[str, list] = {}
    for r in scored:
        by_model.setdefault(r.model_id, []).append(r)
    pairs = [sorted(v, key=lambda r: -r.score) for v in by_model.values() if len(v) > 1]
    if pairs:
        pair = max(pairs, key=lambda p: p[0].score - p[-1].score)
        a, b = pair[0], pair[-1]
        parts.append(
            '<div class="split"><div><h3>Same model, different app</h3>'
            f'<p>{esc(_short(a, by_id))} and {esc(_short(b, by_id))} run the same model, so their benchmark scores '
            f'are identical. In the app, {esc(_short(a, by_id))} scored {a.layers["B"]:.0f} against '
            f'{b.layers["B"]:.0f}, and the totals ended {a.score:.0f} and {b.score:.0f}.</p></div>'
            + stamp(f"{a.score - b.score:.0f}", label="App effect", unit="Points", tone="red", size="s")
            + "</div>")

    if edition.get("takeaway"):
        parts.append(f'<p class="lede"><strong>{esc(edition["takeaway"])}.</strong> '
                     f'{esc(edition.get("takeaway_standfirst", ""))}</p>')
    pdf = f"output/editions/{ed_dir.name}/everyday-ai-index-ed{edition['number']}.pdf"
    parts.append(f'<p class="note">Carousel PDF and raw scores: <a href="{REPO_URL}/{pdf}" target="_blank" '
                 f'rel="noopener">{esc(pdf)}</a></p>')
    return f'<div data-ed-panel="{_edition_id(edition)}" id="{_edition_id(edition)}">{"".join(parts)}</div>'


def _benchmark_rows() -> str:
    with (ROOT / "config" / "benchmarks.toml").open("rb") as f:
        cfg = tomllib.load(f)
    rows = []
    for sid, slot in cfg["slots"].items():
        if slot.get("weight", 0) <= 0:
            continue
        names = [b["name"] for b in cfg["benchmarks"] if b["slot"] == sid and b.get("status") == "active"]
        rows.append(f'<tr><td>{esc(slot["name"])}</td><td>{esc("; ".join(names))}</td>'
                    f'<td class="num">{slot["weight"] * 100:.0f}%</td></tr>')
    return "".join(rows), cfg.get("last_reviewed", "")


def site_html(editions, weights_cfg) -> str:
    """editions: list of (edition, profile, results, warnings, setups, ed_dir), oldest first."""
    light, dark = token_vars("light"), token_vars("dark")
    color_keys = [k for k in light if k in dark and light[k] != dark[k]]
    dark_only = {k: dark[k] for k in color_keys}
    css = (css_block(":root", light)
           + "@media (prefers-color-scheme: dark) {\n"
           + css_block(':root:not([data-theme="light"])', {**dark_only, "color-scheme": "dark"}) + "}\n"
           + css_block(':root[data-theme="dark"]', {**dark_only, "color-scheme": "dark"}))

    layers = weights_cfg["profiles"]["everyday"]["layers"]
    layer_rows = sorted(layers.items(), key=lambda kv: -kv[1])
    harness = sorted(weights_cfg["harness"].values(), key=lambda d: -d["weight"])
    g = weights_cfg["gates"]
    bench_rows, reviewed = _benchmark_rows()
    latest = editions[-1] if editions else None

    ed_nav = ""
    if len(editions) > 1:
        ed_nav = '<div class="ed-nav" role="group" aria-label="Editions">' + "".join(
            f'<button type="button" data-ed="{_edition_id(e[0])}" aria-pressed="{str(e is latest).lower()}">'
            f'Ed. {e[0]["number"]}</button>' for e in reversed(editions)) + "</div>"
    panels = "".join(
        _edition_section(*e, weights_cfg).replace("<div data-ed-panel", "<div hidden data-ed-panel", 1)
        if e is not latest else _edition_section(*e, weights_cfg) for e in editions)
    updated = (dt.date.fromisoformat(str(latest[0]["date"])).strftime("%-d %B %Y") if latest else "")

    harness_help = {
        "Gets it done end-to-end": "From request to a usable file, draft or result, without copy-pasting between apps.",
        "Built-in tools": "Web search with citations, reading PDFs and spreadsheets, running code, making files.",
        "Connects to your stuff": "Email, calendar, drive, notes, and an open connector standard for the rest.",
        "Remembers context": "Projects, memory and long conversations that don't fall apart.",
        "Recovers from mistakes": "Notices its own errors, checks its work, doesn't loop when corrected.",
        "Safe control": "Asks before anything irreversible; undo and a clear record of what it did.",
        "Speed and reliability": "Fast, rarely down, rarely capped, never cuts off a long answer.",
        "Works everywhere you are": "Web, desktop, phone and voice, with history that syncs.",
        "Low learning curve": "Good results from a plain request, without prompt tricks.",
    }

    body = f"""
<title>Everyday AI Index</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400..900&family=Archivo+Narrow:wght@400..700&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&display=swap">
<style>
{css}
{bundle_css()}
{PAGE_CSS}
</style>
<main class="page">
  <span class="page-tab" aria-hidden="true"></span>
  <header class="top">
    <div>
      <p class="kicker" style="margin-top:28px">Everyday AI Index</p>
      <h1>The benchmark is not the job</h1>
      <p class="standfirst">The AI that tops the leaderboard is often not the one that gets my work done. This index scores
      AI the way I use it: a model inside an app, tested on my own errands, with the app counted as much as the model.</p>
    </div>
    <div class="stamp-slot">{stamp(f"{layers['B'] * 100:.0f}", label="App share", unit="Percent", tone="green", size="s")}</div>
  </header>
  <div class="byline"><strong>Evan van Dongen</strong><span>Updated {esc(updated)}</span>
    <span>{len(editions)} edition{"s" if len(editions) != 1 else ""}</span><span>Re-run with every major model release</span></div>

  <section aria-labelledby="results">
    <p class="kicker" id="results">Latest results</p>
    {ed_nav}
    {panels}
  </section>

  <section aria-labelledby="why">
    <p class="kicker">Why</p>
    <h2 id="why">High scores, low usefulness</h2>
    <p class="lede">Some models rank near the top of every leaderboard and still feel weaker in daily use. Nobody needs
    to be cheating for that to happen.</p>
    <ul class="list">
      {"".join(f'<li><span class="name">{esc(a)}</span><span class="desc">{esc(b)}</span></li>' for a, b in CAUSES)}
    </ul>
    <p class="note">It cuts both ways: a research harness built to win Terminal-Bench beats the everyday app running the
    same Claude model. Winning a test and being pleasant and safe to use are different things, so the index scores them separately.</p>
  </section>

  <section aria-labelledby="how">
    <p class="kicker">How</p>
    <h2 id="how">Four layers, one score</h2>
    <p class="lede">I rate a <strong>setup</strong>: a model plus the app I reach it through. The same model in two apps
    counts as two setups. Each layer is scored against the best setup in the edition, so the scale never tops out.</p>
    <figure class="figure"><p class="figure-sub">Weight in the everyday profile, %</p>
      {_bars([(LAYER_NAMES[k], v * 100) for k, v in layer_rows], highlight={LAYER_NAMES["B"]}, unit="%", max_value=40)}
    </figure>
    <ul class="list">
      {"".join(f'<li><span class="name">{esc(LAYER_NAMES[k])}</span><span class="val">{v * 100:.0f}%</span><span class="desc">{esc(LAYER_HELP[k])}</span></li>' for k, v in layer_rows)}
    </ul>
  </section>

  <section aria-labelledby="app">
    <div class="split"><div><p class="kicker">The app</p><h2 id="app">Nine things I check</h2></div>
      <div class="icon-tile">{icon("cog", 72)}</div></div>
    <p class="lede">Each scored 0 to 4 against things I can observe, so two people scoring the same app land within a point.</p>
    <ul class="list">
      {"".join(f'<li><span class="name">{esc(d["name"])}</span><span class="val">{d["weight"] * 100:.0f}%</span><span class="desc">{esc(harness_help.get(d["name"], ""))}</span></li>' for d in harness)}
    </ul>
  </section>

  <section aria-labelledby="tests">
    <div class="split"><div><p class="kicker">The tests</p><h2 id="tests">Nobody can train on my tasks</h2></div>
      {stamp("0", label="Target", unit="Minutes", tone="green", size="s")}</div>
    <p class="lede">Twelve errands from my own month, from replying to a formal letter to reading a 60-page contract.
    Each one runs in every app. A script hides the names and shuffles the answers before I grade them.</p>
    <p>The number I care about most is <strong>minutes of my time per finished task</strong>, prompting, checking and
    fixing included. It never maxes out: a better AI just pushes it towards zero. When an AI fails me on something
    real, that task joins the list; once every app passes a task twice, it retires.</p>
  </section>

  <section aria-labelledby="gates">
    <p class="kicker">The gates</p>
    <h2 id="gates">Some flaws can't be outscored</h2>
    <p class="lede">These multiply the score instead of adding to it, so being brilliant elsewhere doesn't buy them back.</p>
    <div class="table-wrap"><table class="data"><thead><tr><th>Gate</th><th>What it checks</th><th class="num">Concern</th><th class="num">Fail</th></tr></thead><tbody>
      <tr><td>Privacy</td><td>Where my data goes, whether it trains on it, which country's law applies</td><td class="num">×{g["concern"]}</td><td class="num">×{g["fail"]}</td></tr>
      <tr><td>Reliability</td><td>There when I need it, without caps or outages</td><td class="num">×{g["concern"]}</td><td class="num">×{g["fail"]}</td></tr>
      <tr><td>Honesty</td><td>Invented sources in my own tests: 1–2 is a concern, 3 or more a fail</td><td class="num">×{g["concern"]}</td><td class="num">×{g["fail"]}</td></tr>
    </tbody></table></div>
  </section>

  <section aria-labelledby="bench">
    <p class="kicker">The model layer</p>
    <h2 id="bench">Benchmarks in use</h2>
    <p class="lede">Only independently run tests of finished work. Each one fills a permanent slot; when a test
    saturates or leaks, it is swapped and the slot's weight stays the same.</p>
    <div class="table-wrap"><table class="data"><thead><tr><th>Slot</th><th>Current benchmark</th><th class="num">Weight</th></tr></thead>
      <tbody>{bench_rows}</tbody></table></div>
    <p class="figure-source">Left out on purpose: MMLU, GPQA, AIME, Humanity's Last Exam and HumanEval. Slots last reviewed {esc(reviewed)}.</p>
  </section>

  <section aria-labelledby="last">
    <div class="split"><div><p class="kicker">Built to last</p><h2 id="last">It outlasts the models</h2></div>
      <div class="icon-tile">{icon("idea", 72)}</div></div>
    <ul class="list">
      <li><span class="name">Skills stay fixed. The tests that measure them get swapped.</span><span class="desc">"Doesn't make things up" will matter in 2030, long after today's hallucination benchmark is retired.</span></li>
      <li><span class="name">A test retires once the leader passes 90%,</span><span class="desc">or when the top three sit within noise, when it leaks into training data, or when only vendors still report it.</span></li>
      <li><span class="name">Scores are relative.</span><span class="desc">The best setup in each edition sets 100, so the index never maxes out as everything improves.</span></li>
      <li><span class="name">Two numbers mean the same thing forever.</span><span class="desc">My minutes per finished task, and the longest task an AI can finish on its own.</span></li>
    </ul>
  </section>

  <section aria-labelledby="sources">
    <p class="kicker">Sources</p>
    <h2 id="sources">Where the numbers come from</h2>
    <ul class="list">
      {"".join(f'<li><a class="name" href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a></li>' for t, u in SOURCES)}
    </ul>
    <p class="note">Written with Claude, an Anthropic model, which is one reason my own blind tests and an observable
    checklist carry most of the weight. Method, weights and scorer are open: <a href="{REPO_URL}" target="_blank" rel="noopener">everyday-ai-index on GitHub</a>.</p>
  </section>

  <footer class="end"><strong>EVAN VAN DONGEN</strong><span>Everyday AI Index · method v1</span></footer>
</main>
{SCRIPT}
"""
    return body.strip() + "\n"
