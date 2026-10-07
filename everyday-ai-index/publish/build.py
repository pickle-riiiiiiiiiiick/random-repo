#!/usr/bin/env python3
"""Build the LinkedIn carousels and the web page for the Everyday AI Index.

    python3 publish/build.py                  # rebuild everything: method deck, every edition, web page
    python3 publish/build.py new 2026-11-gpt6 # start a new edition from the latest one
    python3 publish/build.py edition editions/001-2026-11-gpt6
    python3 publish/build.py method
    python3 publish/build.py site

Outputs go to everyday-ai-index/output/:
    method/everyday-ai-index-method.pdf             evergreen carousel
    editions/<slug>/everyday-ai-index-ed<N>.pdf     one results carousel per edition
    editions/<slug>/cover.png                       slide 1 as an image (preview / single-image post)
    site/index.html                                 the shareable web page
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import score  # noqa: E402
from ds import deck_html  # noqa: E402
from slides import method_deck, results_deck  # noqa: E402

EDITIONS = ROOT / "editions"
OUTPUT = ROOT / "output"
CSV_FILES = ["setups.csv", "public_scores.csv", "harness_scores.csv", "personal_results.csv"]


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def weights() -> dict:
    return load_toml(ROOT / "config" / "weights.toml")


def render(html: str, html_path: Path, pdf_path: Path, *, cover_png: Path | None = None,
           png_dir: Path | None = None) -> None:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    cmd = ["node", str(HERE / "render.cjs"), str(html_path), str(pdf_path)]
    if cover_png:
        cmd += ["--cover-png", str(cover_png)]
    if png_dir:
        cmd += ["--png-dir", str(png_dir)]
    subprocess.run(cmd, check=True)


def asset_prefix(from_dir: Path) -> str:
    """Relative path from a generated HTML file's folder to publish/assets/."""
    import os
    return os.path.relpath(HERE / "assets", from_dir).replace(os.sep, "/") + "/"


# ----------------------------------------------------------------- editions ---

def list_editions() -> list[Path]:
    return sorted(p for p in EDITIONS.iterdir() if (p / "edition.toml").exists()) if EDITIONS.exists() else []


def score_edition(ed_dir: Path):
    edition = load_toml(ed_dir / "edition.toml")
    profile, results, warnings = score.compute(
        ed_dir, ROOT / "config", ROOT / "tasks" / "personal_battery.toml", edition.get("profile"))
    setups = score.load_csv(ed_dir / "setups.csv")
    return edition, profile, results, warnings, setups


def build_edition(ed_dir: Path, png_dir: Path | None = None) -> Path:
    edition, profile, results, warnings, setups = score_edition(ed_dir)
    for w in warnings:
        print(f"  warning: {w}")
    slides = results_deck(edition, profile, results, setups, weights())
    out = OUTPUT / "editions" / ed_dir.name
    html_path = OUTPUT / "_build" / f"{ed_dir.name}.html"
    pdf = out / f"everyday-ai-index-ed{edition['number']}.pdf"
    render(deck_html(slides, title=f"Everyday AI Index, edition {edition['number']}",
                     asset_prefix=asset_prefix(html_path.parent)),
           html_path, pdf, cover_png=out / "cover.png", png_dir=png_dir)
    (out / "scores.md").write_text(score.render_markdown(profile, results, warnings) + "\n", encoding="utf-8")
    return pdf


def build_method(png_dir: Path | None = None) -> Path:
    html_path = OUTPUT / "_build" / "method.html"
    pdf = OUTPUT / "method" / "everyday-ai-index-method.pdf"
    render(deck_html(method_deck(weights()), title="Everyday AI Index: the method",
                     asset_prefix=asset_prefix(html_path.parent)),
           html_path, pdf, cover_png=OUTPUT / "method" / "cover.png", png_dir=png_dir)
    return pdf


def build_site() -> Path:
    from site_page import site_html
    editions = [score_edition(p) + (p,) for p in list_editions()]
    out = OUTPUT / "site" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(site_html(editions, weights()), encoding="utf-8")
    return out


def new_edition(slug: str, src: Path | None) -> Path:
    existing = list_editions()
    src = src or (existing[-1] if existing else ROOT / "data")
    number = max((load_toml(p / "edition.toml").get("number", 0) for p in existing), default=-1) + 1
    dest = EDITIONS / f"{number:03d}-{slug}"
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    dest.mkdir(parents=True)
    for name in CSV_FILES:
        if (src / name).exists():
            shutil.copyfile(src / name, dest / name)
    # Personal results are per run: start the new edition with an empty sheet.
    (dest / "personal_results.csv").write_text("setup_id,task_id,outcome,minutes,nudges,errors,invented_source\n")
    (dest / "edition.toml").write_text(
        f'number = {number}\n'
        f'date = "{dt.date.today().isoformat()}"\n'
        'trigger = "What prompted this run, e.g. New model: <name> released <date>"\n'
        "illustrative = false\n"
        'profile = "everyday"\n'
        '# highlight = "S1"\n\n'
        'headline = "Six words or fewer, a claim"\n'
        'standfirst = "One or two sentences on what changed this round."\n'
        'ranking_title = "Who gets it done"\n'
        'takeaway = "The one-line lesson"\n'
        'takeaway_standfirst = "Why it matters, with a number."\n',
        encoding="utf-8")
    print(f"created {dest} (copied data from {src}). Next:")
    print("  1. update setups.csv (add the new model/app), public_scores.csv and harness_scores.csv")
    print("  2. run your task battery, grade blind (blind.py), save personal_results.csv")
    print("  3. write the headline and takeaway in edition.toml")
    print(f"  4. python3 publish/build.py edition {dest.relative_to(ROOT)} && python3 publish/build.py site")
    return dest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--png-dir", type=Path, help="also save every slide as PNG here (for checking layouts)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("all")
    sub.add_parser("method")
    sub.add_parser("site")
    e = sub.add_parser("edition")
    e.add_argument("path", type=Path)
    n = sub.add_parser("new")
    n.add_argument("slug")
    n.add_argument("--from", dest="src", type=Path)
    args = p.parse_args(argv)

    cmd = args.cmd or "all"
    if cmd == "new":
        new_edition(args.slug, args.src)
        return
    if cmd in ("all", "method"):
        print(build_method(args.png_dir and args.png_dir / "method"))
    if cmd == "edition":
        print(build_edition(args.path.resolve(), args.png_dir and args.png_dir / args.path.name))
    if cmd == "all":
        for ed in list_editions():
            print(build_edition(ed, args.png_dir and args.png_dir / ed.name))
    if cmd in ("all", "site"):
        print(build_site())


if __name__ == "__main__":
    main()
