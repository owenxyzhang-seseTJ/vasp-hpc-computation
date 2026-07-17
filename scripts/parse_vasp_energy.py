#!/usr/bin/env python3
"""Parse final VASP energies and convergence hints from OUTCAR/OSZICAR files."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

TOTEN_RE = re.compile(r"free\s+energy\s+TOTEN\s+=\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)")
F_RE = re.compile(r"F=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)")

CONV_MARKERS = [
    "reached required accuracy",
    "General timing and accounting informations",
    "Voluntary context switches",
]
ERROR_PATTERNS = [
    "ZBRENT",
    "EDDDAV",
    "BRMIX",
    "Sub-Space-Matrix is not hermitian",
    "ERROR",
    "Error",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except FileNotFoundError:
        return ""


def parse_outcar(path: Path) -> dict:
    text = read_text(path)
    energies = [float(x) for x in TOTEN_RE.findall(text)]
    lower = text.lower()
    converged = any(marker.lower() in lower for marker in CONV_MARKERS)
    errors = [pat for pat in ERROR_PATTERNS if pat in text]
    return {
        "path": str(path),
        "energy_ev": energies[-1] if energies else None,
        "num_ionic_steps": len(energies),
        "converged_hint": converged,
        "errors": ";".join(errors),
    }


def parse_oszicar(path: Path) -> dict:
    text = read_text(path)
    energies = [float(x) for x in F_RE.findall(text)]
    return {
        "path": str(path),
        "energy_ev": energies[-1] if energies else None,
        "num_ionic_steps": len(energies),
        "converged_hint": bool(energies),
        "errors": "",
    }


def collect(root: Path) -> list[dict]:
    rows = []
    outcars = sorted(root.rglob("OUTCAR"))
    if outcars:
        rows.extend(parse_outcar(p) for p in outcars)
    else:
        rows.extend(parse_oszicar(p) for p in sorted(root.rglob("OSZICAR")))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse VASP final energies from OUTCAR files.")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("-o", "--output", default="vasp_energies.csv", help="Output CSV path")
    args = parser.parse_args()

    rows = collect(Path(args.root))
    fields = ["path", "energy_ev", "num_ionic_steps", "converged_hint", "errors"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output} with {len(rows)} rows")


if __name__ == "__main__":
    main()
