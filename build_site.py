#!/usr/bin/env python3
"""Build the minimal static artifact deployed by GitHub Pages."""

from __future__ import annotations

import shutil
from pathlib import Path

import build


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "_site"
PUBLIC_PATHS = (
    ROOT / "assets",
    ROOT / "styles.css",
    ROOT / "script.js",
    ROOT / "robots.txt",
    ROOT / ".nojekyll",
)


def main() -> int:
    projects = build.load_projects()
    pages = build.build_outputs(projects)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    for source, contents in pages.items():
        destination = OUTPUT_DIR / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(contents, encoding="utf-8")

    for source in PUBLIC_PATHS:
        destination = OUTPUT_DIR / source.relative_to(ROOT)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store"))
        else:
            shutil.copy2(source, destination)

    print(f"Built {len(projects)} projects in {OUTPUT_DIR.relative_to(ROOT)}/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
