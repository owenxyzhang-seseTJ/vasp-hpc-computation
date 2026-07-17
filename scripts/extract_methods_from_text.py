#!/usr/bin/env python3
"""Extract computational-method hints from literature text using regex heuristics."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

KEYS = {
    "software": [r"RASPA", r"VASP\s*\d*(?:\.\d+)*", r"PSI4", r"ORCA", r"Gaussian", r"CP2K"],
    "functionals": [r"PBE(?:-D3BJ|-D3)?", r"B3LYP", r"SCAN", r"r2SCAN", r"M06-2X"],
    "dispersion": [r"D3BJ", r"D3", r"D4", r"Grimme", r"vdW-DF"],
    "force_fields": [r"UFF", r"TraPPE", r"DREIDING", r"OPLS", r"COMPASS"],
    "charges": [r"DDEC\d*", r"REPEAT", r"Mulliken", r"Bader", r"CM5"],
    "methods": [r"canonical Monte[- ]Carlo", r"GCMC", r"CI-NEB", r"NEB", r"MP2\.5", r"MP2", r"counterpoise", r"BSSE"],
    "parameters": [r"\d+\s*eV", r"\d+\s*[x×]\s*\d+\s*[x×]\s*\d+", r"\d+\.?\d*\s*eV\s*\.?\s*[ÅA]-1", r"\d+\s*[x×]\s*10\^?\d+\s*cycles"],
}


def extract(text: str) -> dict:
    out = {}
    for key, pats in KEYS.items():
        found = []
        for pat in pats:
            found.extend(re.findall(pat, text, flags=re.I))
        out[key] = sorted({str(x) for x in found})
    formulas = re.findall(r"[A-Z][A-Za-z0-9_{}()\s+\-.]*=\s*E\([^\n]+", text)
    out["energy_formula_candidates"] = formulas[:10]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract computational method hints from a text file.")
    parser.add_argument("textfile")
    parser.add_argument("-o", "--output", default="method_hints.json")
    args = parser.parse_args()
    text = Path(args.textfile).read_text(errors="ignore")
    out = extract(text)
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
