#!/usr/bin/env python3
"""Heuristically parse common RASPA loading and energy lines from text outputs."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PATTERNS = {
    "absolute_loading": re.compile(r"Average loading absolute\s+\[.*?\]\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)", re.I),
    "excess_loading": re.compile(r"Average loading excess\s+\[.*?\]\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)", re.I),
    "host_guest_energy": re.compile(r"Host-adsorbate energy:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)", re.I),
    "total_energy": re.compile(r"Total energy:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)", re.I),
}


def parse_file(path: Path) -> dict:
    text = path.read_text(errors="ignore")
    row = {"path": str(path)}
    for key, pat in PATTERNS.items():
        vals = pat.findall(text)
        row[key] = vals[-1] if vals else ""
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse common RASPA output quantities.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("-o", "--output", default="raspa_summary.csv")
    args = parser.parse_args()
    root = Path(args.root)
    files = sorted(root.rglob("*.data")) + sorted(root.rglob("*.out")) + sorted(root.rglob("output*"))
    rows = [parse_file(p) for p in files if p.is_file()]
    fields = ["path", "absolute_loading", "excess_loading", "host_guest_energy", "total_energy"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output} with {len(rows)} rows")


if __name__ == "__main__":
    main()
