#!/usr/bin/env python3
"""Everyday AI Index scorer.

Combines public benchmarks (Layer A), a harness-usability rubric (Layer B),
your own blind task results (Layer C) and cost/friction (Layer D) into one
score per *setup* (model + the product you use it through), then applies
privacy / reliability / honesty gates.

Every layer is scored relative to the best setup in the field you are
comparing (best = 100), so the index never saturates as models improve.

Usage:
    python3 score.py --data data/example
    python3 score.py --data data --profile developer --json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE_LEVELS = ("pass", "concern", "fail")
MIN_COVERAGE = 0.7


# ---------------------------------------------------------------- loading ---

def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            # Skip blank lines and comment rows.
            if not any((v or "").strip() for v in row.values()):
                continue
            first = next(iter(row.values())) or ""
            if first.strip().startswith("#"):
                continue
            rows.append({k.strip(): (v or "").strip() for k, v in row.items() if k})
        return rows


def to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


# ---------------------------------------------------------- normalisation ---

def normalise(value: float, best: float, scale: str) -> float:
    """Map a raw value to 0-100 relative to the best value in the field."""
    if scale == "ratio":
        return 0.0 if best <= 0 else max(0.0, min(100.0, value / best * 100))
    if scale == "inverse_ratio":  # lower is better; `best` is the minimum
        if value <= 0:
            return 100.0
        return max(0.0, min(100.0, best / value * 100))
    if scale == "elo":
        p_win = 1 / (1 + 10 ** ((best - value) / 400))
        return 200 * p_win
    if scale == "log":
        if value <= 0 or best <= 0:
            return 0.0
        doublings_behind = math.log2(best / value)
        return max(0.0, 100 - 25 * doublings_behind)
    raise ValueError(f"unknown scale {scale!r}")


def best_of(values: list[float], scale: str) -> float:
    return min(values) if scale == "inverse_ratio" else max(values)


def weighted_mean(pairs: list[tuple[float, float]]) -> float | None:
    """pairs = [(score, weight)]; returns None if no weight."""
    total_w = sum(w for _, w in pairs)
    if total_w <= 0:
        return None
    return sum(s * w for s, w in pairs) / total_w


# ------------------------------------------------------------------ model ---

@dataclass
class SetupResult:
    setup_id: str
    label: str
    model_id: str
    layers: dict[str, float | None] = field(default_factory=dict)
    coverage: dict[str, float] = field(default_factory=dict)
    gates: dict[str, str] = field(default_factory=dict)
    gate_multiplier: float = 1.0
    base_score: float | None = None
    score: float | None = None
    overall_coverage: float = 0.0
    provisional: bool = False
    anchors: dict[str, float | None] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def resolve_profile(weights_cfg: dict, name: str | None) -> tuple[str, dict]:
    name = name or weights_cfg.get("default_profile", "everyday")
    profiles = weights_cfg.get("profiles", {})
    if name not in profiles:
        raise SystemExit(f"unknown profile {name!r}; choose from {', '.join(profiles)}")
    return name, profiles[name]


# ---------------------------------------------------------------- layer A ---

def score_layer_a(setups, public_rows, bench_cfg, profile, warnings):
    slot_weights = {sid: s.get("weight", 0.0) for sid, s in bench_cfg["slots"].items()}
    slot_weights.update(profile.get("slot_weights", {}))
    total_slot_w = sum(w for w in slot_weights.values() if w > 0)

    benches = {b["id"]: b for b in bench_cfg.get("benchmarks", [])}
    models_in_field = {s["model_id"] for s in setups}

    # raw[benchmark_id][model_id] = value (latest row wins)
    raw: dict[str, dict[str, float]] = {}
    for row in public_rows:
        bid, mid, val = row.get("benchmark_id"), row.get("model_id"), to_float(row.get("value"))
        if bid not in benches:
            warnings.add(f"public_scores: unknown benchmark_id {bid!r} ignored")
            continue
        if benches[bid].get("status") == "retired":
            warnings.add(f"public_scores: {bid!r} is retired and was ignored")
            continue
        if val is None or mid not in models_in_field:
            continue
        raw.setdefault(bid, {})[mid] = val

    norm: dict[str, dict[str, float]] = {}
    for bid, by_model in raw.items():
        scale = benches[bid]["scale"]
        best = best_of(list(by_model.values()), scale)
        norm[bid] = {m: normalise(v, best, scale) for m, v in by_model.items()}

    results = {}
    for s in setups:
        mid = s["model_id"]
        slot_scores = []
        for sid, w in slot_weights.items():
            if w <= 0:
                continue
            vals = [norm[b][mid] for b, cfg in benches.items()
                    if cfg["slot"] == sid and b in norm and mid in norm[b]]
            if vals:
                slot_scores.append((sum(vals) / len(vals), w))
        covered = sum(w for _, w in slot_scores)
        results[s["setup_id"]] = (
            weighted_mean(slot_scores),
            covered / total_slot_w if total_slot_w else 0.0,
            raw.get("metr_horizon_50_hours", {}).get(mid),
        )
    return results


# ---------------------------------------------------------------- layer B ---

def score_layer_b(setups, harness_rows, weights_cfg, profile):
    dims = {k: v["weight"] for k, v in weights_cfg["harness"].items()}
    dims.update(profile.get("harness_weights", {}))
    total_w = sum(dims.values())
    by_setup = {r["setup_id"]: r for r in harness_rows}

    raw = {}
    for s in setups:
        row = by_setup.get(s["setup_id"], {})
        pairs = []
        for dim, w in dims.items():
            v = to_float(row.get(dim))
            if v is not None:
                pairs.append((max(0.0, min(4.0, v)) / 4 * 100, w))
        raw[s["setup_id"]] = (weighted_mean(pairs), sum(w for _, w in pairs) / total_w)

    present = [v for v, _ in raw.values() if v is not None]
    best = max(present) if present else 0
    return {sid: (None if v is None else normalise(v, best, "ratio"), cov, v)
            for sid, (v, cov) in raw.items()}


# ---------------------------------------------------------------- layer C ---

def score_layer_c(setups, result_rows, battery, weights_cfg):
    tasks = {t["id"]: t for t in battery.get("tasks", []) if t.get("status", "active") == "active"}
    total_importance = sum(t.get("importance", 1) for t in tasks.values())

    stats = {}
    for s in setups:
        sid = s["setup_id"]
        rows = [r for r in result_rows if r.get("setup_id") == sid and r.get("task_id") in tasks]
        if not rows:
            stats[sid] = None
            continue
        imp_done = quality = minutes = successes = 0.0
        invented = 0
        for r in rows:
            imp = tasks[r["task_id"]].get("importance", 1)
            outcome = max(0.0, min(2.0, to_float(r.get("outcome")) or 0.0))
            imp_done += imp
            quality += imp * outcome / 2
            minutes += to_float(r.get("minutes")) or 0.0
            successes += outcome / 2
            invented += 1 if (to_float(r.get("invented_source")) or 0) > 0 else 0
        stats[sid] = {
            "success_rate": quality / imp_done,
            "minutes_per_success": (minutes / successes) if successes else math.inf,
            "coverage": imp_done / total_importance if total_importance else 0.0,
            "invented_sources": invented,
        }

    present = [v for v in stats.values() if v]
    best_success = max((v["success_rate"] for v in present), default=0)
    finite_mins = [v["minutes_per_success"] for v in present if math.isfinite(v["minutes_per_success"])]
    best_mins = min(finite_mins) if finite_mins else None

    sw = weights_cfg["personal"]["success_weight"]
    ew = weights_cfg["personal"]["efficiency_weight"]
    out = {}
    for sid, v in stats.items():
        if not v:
            out[sid] = (None, 0.0, None)
            continue
        success_score = normalise(v["success_rate"], best_success, "ratio")
        if best_mins is None or not math.isfinite(v["minutes_per_success"]):
            eff_score = 0.0
        else:
            eff_score = normalise(v["minutes_per_success"], best_mins, "inverse_ratio")
        out[sid] = (weighted_mean([(success_score, sw), (eff_score, ew)]), v["coverage"], v)
    return out


# ---------------------------------------------------------------- layer D ---

def score_layer_d(setups, weights_cfg):
    cfg = weights_cfg["cost"]
    k = cfg.get("price_smoothing_usd", 10)
    prices = {s["setup_id"]: to_float(s.get("monthly_cost_usd")) for s in setups}
    limits = {s["setup_id"]: to_float(s.get("limits_0to4")) for s in setups}
    known_prices = [p for p in prices.values() if p is not None]
    cheapest = min(known_prices) if known_prices else None
    known_limits = [v for v in limits.values() if v is not None]
    best_limits = max(known_limits) if known_limits else 0

    out = {}
    for s in setups:
        sid = s["setup_id"]
        pairs = []
        if prices[sid] is not None and cheapest is not None:
            pairs.append(((cheapest + k) / (prices[sid] + k) * 100, cfg["price_weight"]))
        if limits[sid] is not None:
            pairs.append((normalise(limits[sid], best_limits, "ratio"), cfg["limits_weight"]))
        cov = sum(w for _, w in pairs) / (cfg["price_weight"] + cfg["limits_weight"])
        out[sid] = (weighted_mean(pairs), cov)
    return out


# ------------------------------------------------------------------ gates ---

def gate_level(value: str | None) -> str | None:
    v = (value or "").strip().lower()
    return v if v in GATE_LEVELS else None


def apply_gates(setup, personal_stats, weights_cfg, profile):
    gcfg = weights_cfg["gates"]
    gates, notes = {}, []

    g1 = gate_level(setup.get("g1_privacy"))
    if g1 == "concern" and profile.get("strict_privacy"):
        g1 = "fail"
        notes.append("privacy concern treated as fail (strict_privacy profile)")
    gates["G1_privacy"] = g1 or "pass"
    if g1 is None:
        notes.append("G1 privacy not assessed (assumed pass)")

    g2 = gate_level(setup.get("g2_reliability"))
    gates["G2_reliability"] = g2 or "pass"
    if g2 is None:
        notes.append("G2 reliability not assessed (assumed pass)")

    if personal_stats:
        n = personal_stats["invented_sources"]
        g3 = ("fail" if n >= gcfg["honesty_fail_at"]
              else "concern" if n >= gcfg["honesty_concern_at"] else "pass")
    else:
        g3 = gate_level(setup.get("g3_honesty"))
        if g3 is None:
            notes.append("G3 honesty unverified (no personal results)")
    gates["G3_honesty"] = g3 or "pass"

    mult = 1.0
    for level in gates.values():
        mult *= gcfg[level]
    return gates, mult, notes


# ------------------------------------------------------------------- main ---

def compute(data_dir: Path, config_dir: Path, battery_path: Path, profile_name: str | None):
    weights_cfg = load_toml(config_dir / "weights.toml")
    bench_cfg = load_toml(config_dir / "benchmarks.toml")
    battery = load_toml(battery_path) if battery_path.exists() else {"tasks": []}
    profile_name, profile = resolve_profile(weights_cfg, profile_name)

    setups = load_csv(data_dir / "setups.csv")
    if not setups:
        raise SystemExit(f"no setups found in {data_dir / 'setups.csv'}")

    warnings: set[str] = set()
    a = score_layer_a(setups, load_csv(data_dir / "public_scores.csv"), bench_cfg, profile, warnings)
    b = score_layer_b(setups, load_csv(data_dir / "harness_scores.csv"), weights_cfg, profile)
    c = score_layer_c(setups, load_csv(data_dir / "personal_results.csv"), battery, weights_cfg)
    d = score_layer_d(setups, weights_cfg)
    layer_w = profile["layers"]

    results = []
    for s in setups:
        sid = s["setup_id"]
        r = SetupResult(sid, s.get("label", sid), s["model_id"])
        r.layers = {"A": a[sid][0], "B": b[sid][0], "C": c[sid][0], "D": d[sid][0]}
        r.coverage = {"A": a[sid][1], "B": b[sid][1], "C": c[sid][1], "D": d[sid][1]}
        personal = c[sid][2]
        r.anchors = {
            "success_rate_pct": None if not personal else personal["success_rate"] * 100,
            "minutes_per_success": None if not personal else personal["minutes_per_success"],
            "harness_absolute_0to100": b[sid][2],
            "metr_horizon_hours": a[sid][2],
        }

        r.base_score = weighted_mean([(v, layer_w[k]) for k, v in r.layers.items() if v is not None])
        total_lw = sum(layer_w.values())
        r.overall_coverage = sum(layer_w[k] * r.coverage[k] for k in layer_w) / total_lw
        for k, v in r.layers.items():
            if v is None:
                r.notes.append(f"layer {k} has no data; its weight was spread over the others")

        r.gates, r.gate_multiplier, gate_notes = apply_gates(s, personal, weights_cfg, profile)
        r.notes.extend(gate_notes)
        if r.base_score is not None:
            r.score = r.base_score * r.gate_multiplier
        if r.overall_coverage < MIN_COVERAGE:
            r.provisional = True
            r.notes.append(f"coverage {r.overall_coverage:.0%} is below 70%: treat as provisional")
        results.append(r)

    # Provisional (low-coverage) setups rank after fully evidenced ones, so a
    # setup can't climb the table just because a weak layer was never measured.
    results.sort(key=lambda r: (r.provisional, -1 if r.score is None else -r.score))
    return profile_name, results, sorted(warnings)


def fmt(v, spec=".0f", suffix="", empty="–"):
    if v is None:
        return empty
    if isinstance(v, float) and math.isinf(v):
        return "∞"
    return format(v, spec) + suffix


def render_markdown(profile_name, results, warnings) -> str:
    lines = [f"# Everyday AI Index (profile: {profile_name})", ""]
    lines.append("| # | Setup | Score | A Model | B Harness | C Your tasks | D Cost | Gates | Coverage |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        gate_str = "ok" if r.gate_multiplier == 1 else f"×{r.gate_multiplier:.2f}"
        lines.append(
            f"| {i} | {r.label} | **{fmt(r.score)}**{' ⚠' if r.provisional else ''} | {fmt(r.layers['A'])} | {fmt(r.layers['B'])} "
            f"| {fmt(r.layers['C'])} | {fmt(r.layers['D'])} | {gate_str} | {r.overall_coverage:.0%} |"
        )
    lines += ["", "## Absolute anchors (these don't depend on the field)", ""]
    lines.append("| Setup | Success on your tasks | Your minutes per success | Harness rubric (0–100) | METR horizon (h) |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        an = r.anchors
        lines.append(
            f"| {r.label} | {fmt(an['success_rate_pct'], suffix='%')} | {fmt(an['minutes_per_success'], '.1f')} "
            f"| {fmt(an['harness_absolute_0to100'])} | {fmt(an['metr_horizon_hours'], '.1f')} |"
        )
    noted = [r for r in results if r.notes or r.gate_multiplier != 1]
    if noted:
        lines += ["", "## Notes", ""]
        for r in noted:
            failing = [f"{g}={lvl}" for g, lvl in r.gates.items() if lvl != "pass"]
            items = ([f"gates: {', '.join(failing)}"] if failing else []) + r.notes
            lines.append(f"- **{r.label}**: " + "; ".join(items))
    if warnings:
        lines += ["", "## Data warnings", ""] + [f"- {w}" for w in warnings]
    lines += ["", "_Scores are relative to the best setup in this comparison (= 100 per layer). "
              "Gaps under ~5 points are noise. ⚠ = provisional (coverage below "
              f"{MIN_COVERAGE:.0%}), ranked after fully evidenced setups._"]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=HERE / "data", help="folder with the CSV files")
    p.add_argument("--config", type=Path, default=HERE / "config", help="folder with weights.toml and benchmarks.toml")
    p.add_argument("--battery", type=Path, default=HERE / "tasks" / "personal_battery.toml")
    p.add_argument("--profile", help="weighting profile (default from weights.toml)")
    p.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = p.parse_args(argv)

    profile_name, results, warnings = compute(args.data, args.config, args.battery, args.profile)
    if args.json:
        payload = {
            "profile": profile_name,
            "warnings": warnings,
            "results": [
                {**r.__dict__, "anchors": {k: (None if isinstance(v, float) and math.isinf(v) else v)
                                           for k, v in r.anchors.items()}}
                for r in results
            ],
        }
        json.dump(payload, sys.stdout, indent=2)
        print()
    else:
        print(render_markdown(profile_name, results, warnings))


if __name__ == "__main__":
    main()
