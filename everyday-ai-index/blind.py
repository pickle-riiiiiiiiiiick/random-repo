#!/usr/bin/env python3
"""Blind grading helper for the personal task battery (Layer C).

1. Save each setup's output as   outputs/<setup_id>/<task_id>.<ext>
   and log your time per run in  run_log.csv  (setup_id,task_id,minutes,nudges)

2. Anonymise:
       python3 blind.py make outputs/ blinded/
   -> blinded/<task_id>/<random code>.<ext>   (no setup names)
   -> blinded/grading.csv                      (fill in outcome, errors, invented_source)
   -> blinded_key.csv                          (next to blinded/, don't open it until you're done)

3. Grade every file in blinded/ without peeking at the key:
       outcome          0 = unusable, 1 = usable after fixing, 2 = usable as-is
       errors           number of factual/logic mistakes you found
       invented_source  1 if it cited something that doesn't exist, else 0

4. Merge into the scorer's input:
       python3 blind.py merge blinded/ --run-log run_log.csv --out data/personal_results.csv
"""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import string
import sys
from pathlib import Path

RESULT_FIELDS = ["setup_id", "task_id", "outcome", "minutes", "nudges", "errors", "invented_source"]


def key_path(blind_dir: Path) -> Path:
    return blind_dir.parent / f"{blind_dir.name}_key.csv"


def make(src: Path, dst: Path) -> None:
    if dst.exists() and any(dst.iterdir()):
        sys.exit(f"{dst} already exists and is not empty; refusing to overwrite")
    rng = random.SystemRandom()
    entries = []
    for setup_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        for f in sorted(p for p in setup_dir.iterdir() if p.is_file()):
            entries.append((setup_dir.name, f.stem, f))
    if not entries:
        sys.exit(f"no outputs found under {src}/<setup_id>/<task_id>.*")

    rng.shuffle(entries)
    used, key_rows, grading_rows = set(), [], []
    for setup_id, task_id, f in entries:
        code = ""
        while not code or code in used:
            code = "".join(rng.choice(string.ascii_uppercase) for _ in range(4))
        used.add(code)
        out_dir = dst / task_id
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, out_dir / f"{code}{f.suffix}")
        key_rows.append({"task_id": task_id, "code": code, "setup_id": setup_id})
        grading_rows.append({"task_id": task_id, "code": code, "outcome": "", "errors": "", "invented_source": ""})

    grading_rows.sort(key=lambda r: (r["task_id"], r["code"]))
    with (dst / "grading.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["task_id", "code", "outcome", "errors", "invented_source"])
        w.writeheader()
        w.writerows(grading_rows)
    with key_path(dst).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["task_id", "code", "setup_id"])
        w.writeheader()
        w.writerows(key_rows)
    print(f"{len(entries)} outputs anonymised into {dst}/  (key: {key_path(dst)})")


def merge(blind_dir: Path, run_log: Path | None, out: Path) -> None:
    with key_path(blind_dir).open(newline="", encoding="utf-8") as fh:
        key = {(r["task_id"], r["code"]): r["setup_id"] for r in csv.DictReader(fh)}
    runs = {}
    if run_log and run_log.exists():
        with run_log.open(newline="", encoding="utf-8") as fh:
            runs = {(r["setup_id"], r["task_id"]): r for r in csv.DictReader(fh)}

    rows, ungraded = [], 0
    with (blind_dir / "grading.csv").open(newline="", encoding="utf-8") as fh:
        for g in csv.DictReader(fh):
            if not g.get("outcome", "").strip():
                ungraded += 1
                continue
            setup_id = key[(g["task_id"], g["code"])]
            run = runs.get((setup_id, g["task_id"]), {})
            rows.append({
                "setup_id": setup_id,
                "task_id": g["task_id"],
                "outcome": g["outcome"],
                "minutes": run.get("minutes", ""),
                "nudges": run.get("nudges", ""),
                "errors": g.get("errors", ""),
                "invented_source": g.get("invented_source", "") or "0",
            })

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=RESULT_FIELDS)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["setup_id"], r["task_id"])))
    print(f"wrote {len(rows)} graded results to {out}" + (f" ({ungraded} still ungraded)" if ungraded else ""))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="anonymise and shuffle outputs")
    m.add_argument("src", type=Path)
    m.add_argument("dst", type=Path)
    g = sub.add_parser("merge", help="un-blind grades into personal_results.csv")
    g.add_argument("blind_dir", type=Path)
    g.add_argument("--run-log", type=Path)
    g.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    if args.cmd == "make":
        make(args.src, args.dst)
    else:
        merge(args.blind_dir, args.run_log, args.out)


if __name__ == "__main__":
    main()
