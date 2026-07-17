#!/usr/bin/env python3
"""Batch classify VASP calculation folders."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

KNOWN_ERRORS = {
    "ZBRENT": "line_search_or_geometry_issue",
    "EDDDAV": "electronic_diagonalization_issue",
    "BRMIX": "charge_mixing_issue",
    "Sub-Space-Matrix is not hermitian": "electronic_issue",
}


def classify(folder: Path) -> dict:
    outcar = folder / "OUTCAR"
    oszicar = folder / "OSZICAR"
    contcar = folder / "CONTCAR"
    if not outcar.exists() and not oszicar.exists():
        return {"folder": str(folder), "status": "not_started", "reason": "no OUTCAR/OSZICAR", "suggestion": "check submission"}
    text = outcar.read_text(errors="ignore") if outcar.exists() else oszicar.read_text(errors="ignore")
    if "reached required accuracy" in text:
        return {"folder": str(folder), "status": "converged", "reason": "accuracy marker found", "suggestion": "parse energy"}
    for pattern, reason in KNOWN_ERRORS.items():
        if pattern in text:
            return {"folder": str(folder), "status": "failed_known", "reason": reason, "suggestion": "inspect and apply minimal repair after approval"}
    if contcar.exists() and contcar.stat().st_size > 0:
        return {"folder": str(folder), "status": "incomplete", "reason": "CONTCAR exists but no convergence marker", "suggestion": "consider restart from CONTCAR"}
    return {"folder": str(folder), "status": "failed_unknown", "reason": "output exists but no known marker", "suggestion": "human review"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify VASP convergence status in subfolders.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("-o", "--output", default="vasp_status.csv")
    args = parser.parse_args()
    root = Path(args.root)
    folders = sorted({p.parent for p in root.rglob("OUTCAR")} | {p.parent for p in root.rglob("OSZICAR")})
    if not folders:
        folders = [root]
    rows = [classify(f) for f in folders]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["folder", "status", "reason", "suggestion"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output} with {len(rows)} rows")


if __name__ == "__main__":
    main()
