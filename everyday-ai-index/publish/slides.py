"""The two LinkedIn carousels.

method_deck()   evergreen: how the index works. Post it once, re-post when the method changes.
results_deck()  one per edition: generated from that edition's scores.
"""

from __future__ import annotations

import math

from ds import bar_chart, esc, icon, post, rows_list, stamp, table

BRAND = "Everyday AI Index"
METHOD_SOURCE = "Full method and scores: link in the comments"

# The harness-swing example on the method cover and slide 2. Same model, same
# benchmark, three agent harnesses. Re-check against the live leaderboard
# before each re-post: these move every few weeks.
HARNESS_SWING = {
    "model": "Claude Opus 4.6",
    "benchmark": "Terminal-Bench 2.0",
    "rows": [("ForgeCode", 81.8), ("Terminus-KIRA", 74.7), ("Claude Code", 58.0)],
    "source": "Source: Terminal-Bench 2.0 via morphllm.com, 2026",
}

LAYER_NAMES = {"A": "Model benchmarks", "B": "App usability", "C": "My blind tests", "D": "Cost and limits"}


def _pages(slides_fns):
    n = len(slides_fns)
    return [fn(f"{i} / {n}") for i, fn in enumerate(slides_fns, 1)]


def _kicker(sub: str) -> str:
    return f"{BRAND} · {sub}"


# ------------------------------------------------------------- method deck ---

def method_deck(weights_cfg: dict) -> list[str]:
    layers = weights_cfg["profiles"]["everyday"]["layers"]
    harness = weights_cfg["harness"]
    rows = sorted(HARNESS_SWING["rows"], key=lambda r: -r[1])
    swing = round(rows[0][1] - rows[-1][1])

    def cover(page):
        return post(
            tone="green", title_size="xl", kicker=_kicker("The method"),
            title="The benchmark is not the job", page=page,
            body=('<div style="flex:1;display:flex;align-items:flex-end;justify-content:space-between;gap:48px">'
                  '<p class="slide-body" style="max-width:15em">Why the AI that tops the leaderboard is often not '
                  'the one that gets my work done, and how I score them instead.</p>'
                  + stamp(str(swing), label="Same model", unit="Points", tone="red", size="l") + "</div>"),
        )

    def swing_slide(page):
        return post(
            kicker=_kicker("Why"), title=f"One model, {swing} points apart",
            standfirst=(f"Same {HARNESS_SWING['model']}, same test, three different apps wrapped around it. "
                        "A leaderboard scores the package, not the model."),
            body=bar_chart(rows, subtitle=f"{HARNESS_SWING['benchmark']} score by agent harness, %",
                           max_value=100, decimals=1, label_width=300)
                 + '<p class="slide-body slide-bottom">The app built to win the test is not the app I use '
                   "every day. So I score the two separately.</p>",
            source=HARNESS_SWING["source"], page=page,
        )

    def layers_slide(page):
        data = sorted(((LAYER_NAMES[k], round(v * 100)) for k, v in layers.items()), key=lambda r: -r[1])
        return post(
            kicker=_kicker("How"), title="Four layers, one score",
            standfirst="I rate the setup: a model plus the app I reach it through. The app gets the biggest share.",
            body=bar_chart(data, subtitle="Weight in the everyday profile, %", highlight={LAYER_NAMES["B"]},
                           unit="%", max_value=40, label_width=330)
                 + '<p class="slide-body slide-bottom">Then three gates: privacy, reliability and honesty. '
                   "Fail one and the score is cut, however good the rest.</p>",
            source="Source: author's method", page=page,
        )

    def harness_slide(page):
        items = sorted(harness.values(), key=lambda d: -d["weight"])
        return post(
            kicker=_kicker("The app"), title="Nine things I check",
            corner_icon=icon("cog", 144),
            standfirst="Scored 0 to 4 against things I can see, like whether it asks before deleting.",
            body=rows_list([(d["name"], f"{round(d['weight'] * 100)}%") for d in items]),
            source="Share of the app-usability score", page=page,
        )

    def tasks_slide(page):
        return post(
            kicker=_kicker("The tests"), title="Nobody can train on my tasks",
            standfirst="Twelve real errands from my own month, run in every app and graded blind with the names hidden.",
            body=('<div class="slide-split"><div>'
                  + rows_list([("Usable as-is?", "0 · 1 · 2"), ("Follow-ups needed", "count"),
                               ("Mistakes I caught", "count"), ("Invented sources", "count")])
                  + '</div>' + stamp("0", label="Target", unit="Minutes", tone="green", size="m",
                                     caption="My time per finished task")
                  + "</div>"
                  '<p class="slide-body slide-bottom">My minutes per finished task is the number that matters '
                  "most. It never maxes out: a better AI just pushes it towards zero.</p>"),
            source="Source: author's method", page=page,
        )

    def gates_slide(page):
        g = weights_cfg["gates"]
        return post(
            kicker=_kicker("The gates"), title="Some flaws can't be outscored",
            corner_icon=icon("target", 144),
            standfirst="These multiply the score instead of adding to it. Being brilliant elsewhere doesn't buy them back.",
            body=table(["Gate", "Concern", "Fail"],
                       [["Privacy: where my data goes", f"×{g['concern']}", f"×{g['fail']}"],
                        ["Reliability: there when I need it", f"×{g['concern']}", f"×{g['fail']}"],
                        ["Honesty: no invented sources", f"×{g['concern']}", f"×{g['fail']}"]]),
            source="Source: author's method", page=page,
        )

    def future_slide(page):
        return post(
            kicker=_kicker("Built to last"), title="It outlasts the models",
            corner_icon=icon("idea", 144),
            standfirst="Most leaderboards die when every model scores 95%. This one is built not to.",
            body=rows_list([
                ("Skills stay fixed. The tests measuring them get swapped.", ""),
                ("A test retires once the leader passes 90%.", ""),
                ("Scores are relative: the best setup sets 100.", ""),
                ("Every time an AI fails me, that task joins the list.", ""),
            ]).replace('<ul class="slide-list">', '<ul class="slide-list slide-list--plain">'),
            source="Source: author's method", page=page,
        )

    def closing(page):
        return post(
            tone="green", title_size="xl", kicker=_kicker("The takeaway"),
            title="Judge the errand, not the exam",
            standfirst="I'll re-run this every time a major model ships, and post the results here.",
            body='<div class="slide-bottom">' + icon("dove", 192) + "</div>",
            source=METHOD_SOURCE, page=page,
        )

    return _pages([cover, swing_slide, layers_slide, harness_slide, tasks_slide, gates_slide, future_slide, closing])


# ------------------------------------------------------------ results deck ---

def _short(r, setups_by_id):
    s = setups_by_id[r.setup_id]
    return s.get("short_label") or (r.label if len(r.label) <= 18 else r.label[:17] + "…")


def results_deck(edition: dict, profile: str, results, setups: list[dict], weights_cfg: dict) -> list[str]:
    by_id = {s["setup_id"]: s for s in setups}
    scored = [r for r in results if r.score is not None]
    if not scored:
        raise SystemExit("no scored setups in this edition")
    winner = scored[0]
    hi_id = edition.get("highlight") or winner.setup_id
    illustrative = edition.get("illustrative", False)
    source = edition.get("source") or "Source: author's tests; public leaderboards"
    if illustrative:
        source = "Source: illustrative data"
    ed_tag = f"Ed. {edition['number']}" + (" · Example" if illustrative else "")
    provisional = [r for r in scored if r.provisional]

    def label(r):
        return _short(r, by_id) + (" *" if r.provisional else "")

    def cover(page):
        return post(
            tone="green", title_size="xl", kicker=_kicker(ed_tag), title=edition["headline"],
            standfirst=edition.get("standfirst", ""), page=page,
            body=('<div style="flex:1;display:flex;align-items:flex-end;justify-content:flex-end">'
                  + stamp(f"{winner.score:.0f}", label="Top score", unit="Of 100", tone="red", size="l")
                  + "</div>"),
            source=("Illustrative data: fictional setups" if illustrative else edition.get("trigger", "")),
        )

    def ranking(page):
        ranked = [r for r in scored if not r.provisional]
        data = [(label(r), round(r.score)) for r in ranked]
        note = ""
        if provisional:
            names = ", ".join(_short(r, by_id) for r in provisional)
            note = f'<p class="slide-note">Not ranked yet, too little data: {esc(names)}.</p>'
        return post(
            kicker=_kicker(ed_tag), title=edition.get("ranking_title", "Who gets it done"),
            standfirst=(f"{_short(winner, by_id)} leads with {winner.score:.0f}. "
                        "The best setup in each round sets the scale."),
            body=bar_chart(data, subtitle=f"Everyday AI Index score, 0–100, {profile} profile",
                           highlight={label(r) for r in ranked if r.setup_id == hi_id},
                           max_value=100, label_width=330) + note,
            source=source, page=page,
        )

    def breakdown(page):
        rows, hi_rows = [], set()
        for i, r in enumerate(scored):
            gate = "–" if r.gate_multiplier == 1 else f"×{r.gate_multiplier:.2f}"
            cells = [label(r)] + [("–" if r.layers[k] is None else f"{r.layers[k]:.0f}") for k in "ABCD"]
            rows.append(cells + [gate, f"{r.score:.0f}"])
            if r.setup_id == hi_id:
                hi_rows.add(i)
        return post(
            kicker=_kicker(ed_tag), title="Where the points come from",
            standfirst="A strong model in a weak app shows up as a high Model score and a low App score.",
            body=table(["Setup", "Model", "App", "Tests", "Cost", "Gates", "Total"], rows, highlight_rows=hi_rows)
                 + '<p class="slide-note">Each column: 100 = best in this round. Gates cut the total for '
                   "privacy, reliability or honesty problems."
                 + (" * Provisional: too little data yet." if provisional else "") + "</p>",
            source=source, page=page,
        )

    def minutes(page):
        rows = [r for r in scored if r.anchors.get("minutes_per_success") is not None
                and math.isfinite(r.anchors["minutes_per_success"])]
        rows.sort(key=lambda r: r.anchors["minutes_per_success"])
        data = [(label(r), round(r.anchors["minutes_per_success"], 1)) for r in rows]
        best = rows[0]
        return post(
            kicker=_kicker(ed_tag), title="Minutes per finished task",
            standfirst=(f"My own time, prompting and fixing included. {_short(best, by_id)} needed "
                        f"{best.anchors['minutes_per_success']:.0f} minutes. Lower is better."),
            body=bar_chart(data, subtitle="Minutes of my time per successful task, my 12-task battery",
                           highlight={label(r) for r in rows if r.setup_id == hi_id}, unit=" min",
                           decimals=0, label_width=330),
            source=source, page=page,
        )

    def same_model(page, a, b):
        gap = round(a.score - b.score)

        def cells(r):
            return [_short(r, by_id)] + [("–" if r.layers[k] is None else f"{r.layers[k]:.0f}")
                                         for k in "ABC"] + [f"{r.score:.0f}"]

        def num(r, k):
            return "–" if r.layers[k] is None else f"{r.layers[k]:.0f}"

        return post(
            kicker=_kicker(ed_tag), title="Same model, different app",
            standfirst="Two setups, one model. Their benchmark scores are identical, so the app made the difference.",
            body=(table(["Setup", "Model", "App", "Tests", "Total"], [cells(a), cells(b)])
                  + '<div class="slide-split slide-bottom"><p class="slide-body">'
                  + esc(f"Same Model score. The app scored {num(a, 'B')} against {num(b, 'B')}, and my own "
                        f"blind tests followed: {num(a, 'C')} against {num(b, 'C')}.")
                  + "</p>" + stamp(str(gap), label="App effect", unit="Points", tone="red", size="m") + "</div>"),
            source=source, page=page,
        )

    def method(page):
        layers = weights_cfg["profiles"][profile]["layers"]
        data = sorted(((LAYER_NAMES[k], round(v * 100)) for k, v in layers.items()), key=lambda r: -r[1])
        return post(
            kicker=_kicker("How it's scored"), title="Four layers, one score",
            standfirst="Public benchmarks are only a quarter of it. The rest is the app, my own blind tests and the price.",
            body=bar_chart(data, subtitle=f"Weight in the {profile} profile, %", unit="%", max_value=40,
                           label_width=330),
            source=METHOD_SOURCE, page=page,
        )

    def closing(page):
        return post(
            tone="green", title_size="xl", kicker=_kicker(ed_tag), title=edition["takeaway"],
            standfirst=edition.get("takeaway_standfirst", ""),
            body='<div class="slide-bottom">' + icon("dove", 192) + "</div>",
            source=METHOD_SOURCE, page=page,
        )

    fns = [cover, ranking, breakdown]
    if any(r.anchors.get("minutes_per_success") for r in scored):
        fns.append(minutes)
    # Same model in two setups: the clearest proof that the app matters.
    by_model: dict[str, list] = {}
    for r in scored:
        by_model.setdefault(r.model_id, []).append(r)
    pairs = [sorted(v, key=lambda r: -r.score) for v in by_model.values() if len(v) > 1]
    if pairs:
        pair = max(pairs, key=lambda p: p[0].score - p[-1].score)
        a, b = pair[0], pair[-1]
        fns.append(lambda page, a=a, b=b: same_model(page, a, b))
    fns += [method, closing]
    return _pages(fns)

