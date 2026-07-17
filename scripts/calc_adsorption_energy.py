#!/usr/bin/env python3
"""Calculate adsorption energies from VASP energies."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

EV_TO_KJMOL = 96.48533212


def load_energy_csv(path: Path) -> dict[str, float]:
    energies: dict[str, float] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("energy_ev") in (None, "", "None"):
                continue
            label = row.get("label") or Path(row.get("path", "")).parent.name
            energies[label] = float(row["energy_ev"])
    return energies


def load_energy_json(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text())
    return {str(k): float(v) for k, v in data.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute adsorption energy from host, guest, and host_guest energies.")
    parser.add_argument("--energies", help="CSV with columns label,energy_ev or JSON mapping labels to energies")
    parser.add_argument("--host", help="Host label or direct energy in eV")
    parser.add_argument("--guest", help="Guest label or direct energy in eV")
    parser.add_argument("--host-guest", dest="host_guest", help="Host+guest label or direct energy in eV")
    parser.add_argument("--n", type=float, default=1.0, help="Number of guest molecules")
    parser.add_argument("-o", "--output", default="adsorption_energy.csv")
    args = parser.parse_args()

    mapping: dict[str, float] = {}
    if args.energies:
        p = Path(args.energies)
        mapping = load_energy_json(p) if p.suffix.lower() == ".json" else load_energy_csv(p)

    def val(token: str | None, name: str) -> float:
        if token is None:
            raise SystemExit(f"missing --{name}")
        try:
            return float(token)
        except ValueError:
            if token not in mapping:
                raise SystemExit(f"label {token!r} not found in energy file")
            return mapping[token]

    e_host = val(args.host, "host")
    e_guest = val(args.guest, "guest")
    e_hg = val(args.host_guest, "host-guest")
    eads_ev = (e_hg - e_host - args.n * e_guest) / args.n
    eads_kjmol = eads_ev * EV_TO_KJMOL

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["E_host_ev", "E_guest_ev", "E_host_guest_ev", "n", "Eads_ev", "Eads_kJ_mol"])
        writer.writeheader()
        writer.writerow({
            "E_host_ev": e_host,
            "E_guest_ev": e_guest,
            "E_host_guest_ev": e_hg,
            "n": args.n,
            "Eads_ev": eads_ev,
            "Eads_kJ_mol": eads_kjmol,
        })
    print(f"Eads = {eads_ev:.6f} eV = {eads_kjmol:.2f} kJ/mol")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
