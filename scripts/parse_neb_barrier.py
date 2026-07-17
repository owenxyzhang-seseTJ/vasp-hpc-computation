#!/usr/bin/env python3
"""Parse VASP NEB image energies and compute a diffusion barrier."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

TOTEN_RE = re.compile(r"free\s+energy\s+TOTEN\s+=\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)")
F_RE = re.compile(r"F=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)")
EV_TO_KJMOL = 96.48533212


def image_dirs(root: Path) -> list[Path]:
    dirs = [p for p in root.iterdir() if p.is_dir() and p.name.isdigit()]
    return sorted(dirs, key=lambda p: int(p.name))


def parse_energy(folder: Path) -> float | None:
    outcar = folder / "OUTCAR"
    oszicar = folder / "OSZICAR"
    if outcar.exists():
        text = outcar.read_text(errors="ignore")
        vals = [float(x) for x in TOTEN_RE.findall(text)]
        if vals:
            return vals[-1]
    if oszicar.exists():
        text = oszicar.read_text(errors="ignore")
        vals = [float(x) for x in F_RE.findall(text)]
        if vals:
            return vals[-1]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute NEB barrier from image OUTCAR/OSZICAR files.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("-o", "--output", default="neb_barrier.csv")
    args = parser.parse_args()

    rows = []
    for d in image_dirs(Path(args.root)):
        e = parse_energy(d)
        rows.append({"image": d.name, "energy_ev": e})
    energies = [r["energy_ev"] for r in rows if r["energy_ev"] is not None]
    if not energies:
        raise SystemExit("no image energies found")
    e0 = energies[0]
    for r in rows:
        if r["energy_ev"] is not None:
            r["relative_ev"] = r["energy_ev"] - e0
            r["relative_kJ_mol"] = r["relative_ev"] * EV_TO_KJMOL
        else:
            r["relative_ev"] = None
            r["relative_kJ_mol"] = None
    barrier_ev = max(energies) - e0
    barrier_kjmol = barrier_ev * EV_TO_KJMOL

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "energy_ev", "relative_ev", "relative_kJ_mol"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"barrier = {barrier_ev:.6f} eV = {barrier_kjmol:.2f} kJ/mol")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
